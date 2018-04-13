from manager import ConnectionManager
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol,listenWS

from models import User


# Our WebSocket Server protocol
class GxgServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print 'onconnect'
        print request.headers
        print("Client connecting: {}".format(request.peer))                  
        tk=request.params
        if tk.get('token'):
            youhu = User.verify_auth_token(tk['token'].pop())
            if not youhu:
                self.dropConnection(abort=True)         
        else:
            self.dropConnection(abort=True)          
        
    def onOpen(self):
        print "open" 
        self.factory.connmanager.addConnection(self)  
        self.factory.register(self)
        self.factory.connmanager.pushObject("servce say open") 
        pass

    def onClose(self, wasClean, code, reason):
        print "onclose"
        self.factory.connmanager.dropConnectionByID(self.transport.sessionno)
        self.unregister(self)
        pass

    def connectionLost(self, reason):  
        print "connlost" 
        self.factory.connmanager.dropConnectionByID(self.transport.sessionno)
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)
        pass

    def onMessage(self, payload, isBinary):
        self.sendMessage(payload, isBinary)

class GxgServerFactory(WebSocketServerFactory):
    protocol = GxgServerProtocol
    def __init__(self, wsuri):
        WebSocketServerFactory.__init__(self, wsuri)
        self.connmanager = ConnectionManager() 
        self.tickcount = 0
        self.tick()

    def tick(self):
        self.tickcount += 1
        self.broadcast("tick %d from server" % self.tickcount)
        reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))
        preparedMsg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(preparedMsg)
            print("prepared message sent to {}".format(c.peer))