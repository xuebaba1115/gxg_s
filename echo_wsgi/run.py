import uuid,os
import sys

from models import db
from protocol import GxgServerFactory,GxgServerProtocol

from twisted.python import log
from twisted.internet import reactor,ssl
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource


from flask_cache import Cache
from flask import Flask, render_template,abort, request, jsonify, g, url_for
from flask.ext import restful

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol,listenWS

from autobahn.twisted.resource import WebSocketResource, WSGIRootResource



# Our WSGI application .. in this case Flask based
app = Flask(__name__)
cache = Cache(app)
app.secret_key = str(uuid.uuid4())




if __name__ == "__main__":

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