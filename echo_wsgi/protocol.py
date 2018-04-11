from manager import ConnectionManager
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol,listenWS



class GxgServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))    
        self.factory.connmanager.addConnection(self)                  
        # print request.headers
        # print request.host
        # print request.path
        # print request.params
        # print request.version
        # print request.origin
        # print request.protocols
        # print request.extensions
        
    
    def onOpen(self):
        self.factory.connmanager.pushObject("servce say open")
        pass

    def onClose(self, wasClean, code, reason):
        self.factory.connmanager.dropConnectionByID(self.transport.sessionno)
        pass

    def connectionLost(self, reason):    
        self.factory.connmanager.dropConnectionByID(self.transport.sessionno)
        pass

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)

class GxgServerFactory(WebSocketServerFactory):
    protocol = GxgServerProtocol
    def __init__(self, wsuri):
        WebSocketServerFactory.__init__(self, wsuri)
        self.connmanager = ConnectionManager()    
        