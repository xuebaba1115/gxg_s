import json
from app.utiles import verify_auth_token
from manager import ConnectionManager
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, listenWS
from twisted.internet.defer import Deferred, \
    inlineCallbacks, returnValue    




# Our WebSocket Server protocol
class GxgServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print 'onconnect'
        print("Client connecting: {}".format(request.peer))
        tk = request.params
        # if tk.get('token'):
        #     youhu = verify_auth_token(tk['token'].pop())
        #     if not youhu:
        #         self.dropConnection(abort=True)
        # else:
        #     self.dropConnection(abort=True)

    def onOpen(self):
        print "open"
        connid = self.factory.connmanager.addConnection(self)
        self.factory.register(self)
        self.factory.connmanager.pushObjectbyconnID(json.dumps(
            {"data": "servce say open %s" % (connid), "connid": connid}))
        pass

    def onClose(self, wasClean, code, reason):
        print "onclose"
        self.factory.unregister(self)
        self.factory.connmanager.dropConnectionByID(self.transport.sessionno)
        pass

    def connectionLost(self, reason):
        print "connlost"
        self.factory.unregister(self)
        self.factory.connmanager.dropConnectionByID(self.transport.sessionno)
        # WebSocketServerProtocol.connectionLost(self, reason)
        pass

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                x = json.loads(payload.decode('utf8'))
                self.sendMessage(json.dumps(x).encode('utf8')) 
            except Exception as e:     
                self.sendMessage(json.dumps(payload).encode('utf8'))         
                self.sendClose(1000, u"Exception raised: {0}".format(e))                             
                pass
    



class GxgServerFactory(WebSocketServerFactory):
    protocol = GxgServerProtocol

    def __init__(self, wsuri):
        WebSocketServerFactory.__init__(self, wsuri)
        self.connmanager = ConnectionManager()
        self.clients = []
        self.tickcount = 0
        self.tick()

    def tick(self):
        self.tickcount += 1
        self.broadcast(json.dumps(
            {"data": "tick %d from server" % self.tickcount}))
        reactor.callLater(60, self.tick)

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
        self.connmanager.pushObjectall(preparedMsg)

    # def broadcast(self, msg):
    #     print("broadcasting prepared message '{}' ..".format(msg))
    #     preparedMsg = self.prepareMessage(msg)
    #     for c in self.clients:
    #         c.sendPreparedMessage(preparedMsg)
    #         print("prepared message sent to {}".format(c.peer))
