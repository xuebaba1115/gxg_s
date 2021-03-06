# coding:utf8
import os
import sys
from app import app, db
from app.protocal import GxgServerFactory, GxgServerProtocol


from twisted.python import log
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, listenWS
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource


if __name__ == "__main__":
    from twisted.internet import reactor, ssl
    # if not os.path.exists('../db.sqlite'):
    #     db.create_all()
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

#curl -i -X POST -H "Content-Type: application/json" -d '{"username":"xlc","password":"xlc"}' http://127.0.0.1:9090/api/users