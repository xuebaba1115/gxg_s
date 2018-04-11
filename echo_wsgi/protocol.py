from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol,listenWS



class GxgServerProtocol(WebSocketServerProtocol):
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

class GxgServerFactory(WebSocketServerFactory):

    protocol = GxgServerProtocol

    def __init__(self, wsuri):
        WebSocketServerFactory.__init__(self, wsuri)
        # self.stats = Stats()        