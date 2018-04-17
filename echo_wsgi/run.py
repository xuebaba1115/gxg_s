import uuid
import sys,os

from utils import WXBizDataCrypt

from twisted.python import log
from twisted.internet import reactor,ssl
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource


from flask import Flask, render_template,abort, request, jsonify, g, url_for,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth


from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol,listenWS
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource



# Our WSGI application .. in this case Flask based
app = Flask(__name__)
app.secret_key = str(uuid.uuid4())



#config
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# extensions
auth = HTTPBasicAuth()
db = SQLAlchemy(app)
from models import *




@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True    

@app.route('/')
def page_home():
    return render_template('index.html')

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
    return jsonify({ 'username': user.username })

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/resource')
@auth.login_required
def get_resource():
    token = g.user.generate_auth_token()
    return jsonify({ 'data': 'Hello, %s!' % g.user.username, 'token': token.decode('ascii') })

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route('/api/wxauth')
def wxauth():
    try:
        print request.headers
        qcode=request.headers['X-WX-Code']
        encryptedData=request.headers['X-WX-Encrypted-Data']
        iv=request.headers['X-WX-IV']
    except Exception as e:
        log.msg(str(e))
        abort(400)

    print iv,qcode
    # appId = 'wx4f4bc4dec97d474b'
    # sessionKey = 'tiihtNczf5v6AKRyjwEUhQ=='
    # encryptedData = 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew=='
    # iv = 'r7BXXKkLb8qrSNn05n0qiA=='

    # pc = WXBizDataCrypt(appId, sessionKey)

    # print pc.decrypt(encryptedData, iv)
    return "ssa"


#
if __name__ == "__main__":
    from protocol import GxgServerFactory,GxgServerProtocol

    if not os.path.exists('db.sqlite'):
        db.create_all()

    log.startLogging(sys.stdout)

    contextFactory = ssl.DefaultOpenSSLContextFactory('keys/server.key',
                                                      'keys/server.crt')

    # create a Twisted Web resource for our WebSocket server
    wsFactory = GxgServerFactory(u"wss://127.0.0.1:9000")

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




#  curl -i -X POST -H "Content-Type: application/json" -d '{"username":"xlc3","password":"python"}' http://127.0.0.1:9090/api/users
#  curl -u miguel:python -i -X GET http://127.0.0.1:9090/api/resource

