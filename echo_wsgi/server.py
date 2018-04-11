import uuid
import sys,os

from twisted.python import log
from twisted.internet import reactor,ssl
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource


from flask_cache import Cache
from flask import Flask, render_template,abort, request, jsonify, g, url_for
from flask.ext import restful
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth


from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol,listenWS

from autobahn.twisted.resource import WebSocketResource, WSGIRootResource


# Our WebSocket Server protocol
class EchoServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))
    
    def onOpen(self):
        pass

    def onClose(self, wasClean, code, reason):
        pass

    def connectionLost(self, reason):    
        pass

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)


class HelloWorld(restful.Resource):
    def get(self,todo_id):
        return {'hello': todo_id}        


# Our WSGI application .. in this case Flask based
app = Flask(__name__)
cache = Cache(app)
api = restful.Api(app)
app.secret_key = str(uuid.uuid4())

#config
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
return user



@app.route('/')
@cache.cached(timeout=60)
def page_home():
    return render_template('index.html')

@app.route('/login')
def hello():
    return 'Hello, World!'

@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}


api.add_resource(HelloWorld, '/<string:todo_id>')


if __name__ == "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()

    log.startLogging(sys.stdout)

    contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key',
                                                      'keys/server.crt')

    # create a Twisted Web resource for our WebSocket server
    wsFactory = WebSocketServerFactory(u"wss://127.0.0.1:9000")
    wsFactory.protocol = EchoServerProtocol
    wsResource = WebSocketResource(wsFactory)

    # create a Twisted Web WSGI resource for our Flask server
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

    # create a root resource serving everything via WSGI/Flask, but
    # the path "/ws" served by our WebSocket stuff
    rootResource = WSGIRootResource(wsgiResource, {b'ws': wsResource})

    listenWS(wsFactory, contextFactory)
    

    # create a Twisted Web Site and run everything
    site = Site(rootResource)
    
    # reactor.listenSSL(9090, site, contextFactory)
    reactor.listenTCP(9090, site)
    reactor.run()
