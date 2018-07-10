# coding:utf8
import json
from app.utiles import verify_auth_token
from manager import ConnectionManager
from game_A import Gamemanger
from game_B import Gamemanger_B
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, listenWS
from twisted.internet.defer import Deferred, \
    inlineCallbacks, returnValue

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# Our WebSocket Server protocol
class GxgServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print 'onconnect'
        print("Client connecting: {}".format(request.peer))
        # tk = request.params
        # if tk.get('token'):
        #     youhu = verify_auth_token(tk['token'].pop())
        #     if not youhu:
        #         self.dropConnection(abort=True)
        # else:
        #     self.dropConnection(abort=True)

    def onOpen(self):
        print "open"

    def onClose(self, wasClean, code, reason):
        print "onclose"
        try:
            self.factory.gamemanger_A.unregister(self.transport.sessionno)
            self.factory.connmanager.dropConnectionByID(
                self.transport.sessionno)
        except Exception as e:
            pass

    def connectionLost(self, reason):
        print "connlost"
        try:
            self.factory.gamemanger_A.unregister(self.transport.sessionno)
            self.factory.connmanager.dropConnectionByID(
                self.transport.sessionno)
        except Exception as e:
            pass

    @inlineCallbacks
    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                x = json.loads(payload.decode('utf8'))
                res = yield self.slowsquare(x)
            except Exception as e:
                self.sendMessage(json.dumps(
                    {"errcode": 1, "errmsg": "%s" % e}).encode('utf8'))

    @inlineCallbacks
    def slowsquare(self, x):
        if x["command"] == "init":
            connid = self.factory.connmanager.addConnection(self)
            pl, allplayers, selfplayers = self.factory.gamemanger_A.register(
                x, connid)
            pl.remove(connid)
            self.factory.connmanager.pushObjectbyconnID(selfplayers, [connid])
            self.factory.broadcast(json.dumps(
                allplayers).encode('utf8'), pl)            
        elif "pid"in x:
            self.factory.gamemanger_B.switch(data=x, conn=self)
            pass

        else:
            aa = yield self.factory.gamemanger_A.handledata(x)
            if aa == None:
                returnValue('')
            else:
                self.factory.broadcast(json.dumps(aa[1]).encode('utf8'), aa[0])
                returnValue('')


class GxgServerFactory(WebSocketServerFactory):
    protocol = GxgServerProtocol

    def __init__(self, wsuri):
        WebSocketServerFactory.__init__(self, wsuri)
        self.connmanager = ConnectionManager()
        self.gamemanger_A = Gamemanger()
        self.gamemanger_B = Gamemanger_B()
        self.tick()

    def tick(self):
        for sendlist, msg in self.gamemanger_A.movebroad("move"):
            if msg["player"] != None:
                self.broadcast(json.dumps(msg).encode('utf8'), sendlist)
        reactor.callLater(0.1, self.tick)

    def broadcast(self, msg, sendlist):
        # print("broadcasting prepared message '{}' ..".format(msg))
        preparedMsg = self.prepareMessage(msg)
        self.connmanager.pushObjectbyconnIDlist(preparedMsg, sendlist)


# test:
# {"command":"init","x":100,"y":210,"name":"xlc","playerType":1,"angle":90}
# {"command":"move","player": {"pos":{"y":500,"x":250},"connid": 1}}
