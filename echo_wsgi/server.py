import uuid
import sys

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask_cache import Cache
from flask import Flask, render_template
from flask.ext import restful

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource, WSGIRootResource


# Our WebSocket Server protocol
class EchoServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

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


@app.route('/')
@cache.cached(timeout=60)
def page_home():
    return render_template('index.html')

@app.route('/login')
def hello():
    return 'Hello, World!'

api.add_resource(HelloWorld, '/<string:todo_id>')


if __name__ == "__main__":

    log.startLogging(sys.stdout)

    # create a Twisted Web resource for our WebSocket server
    wsFactory = WebSocketServerFactory(u"ws://127.0.0.1:8080")
    wsFactory.protocol = EchoServerProtocol
    wsResource = WebSocketResource(wsFactory)

    # create a Twisted Web WSGI resource for our Flask server
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

    # create a root resource serving everything via WSGI/Flask, but
    # the path "/ws" served by our WebSocket stuff
    rootResource = WSGIRootResource(wsgiResource, {b'ws': wsResource})

    # create a Twisted Web Site and run everything
    site = Site(rootResource)

    reactor.listenTCP(8080, site)
    reactor.run()
