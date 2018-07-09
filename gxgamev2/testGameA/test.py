import sys,os
import json
import time
import random
from optparse import OptionParser

from twisted.python import log
from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS


class EchoClientProtocol(WebSocketClientProtocol):
    playerID = None
    y=None
    x=None
    r=None
    flag=True
    def onOpen(self):
        self.y=random.randint(50,200)
        self.x=random.randint(50,200)
        self.r=[0,90,180,270][random.randint(0,3)]
        self.sendMessage(json.dumps(
            {"command":"init","x":self.x,"y":self.y,"name":"xlc","playerType":random.randint(1,2),"angle":self.r}))
        reactor.callLater(5, self.rtang)


    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                x = json.loads(payload.decode('utf8'))
                # print x
                self.analysis(x)
            except Exception as e:
                self.sendMessage(json.dumps(
                    {"errcode": 1, "errmsg": "%s" % e}).encode('utf8'))

    def analysis(self, x):
        if x['command'] =='init' and not self.playerID:
            for p in x['players']:
                self.playerID= p['playerID']
            self.movetank()                

    def rtang(self):
        self.r=[0,90,180,270][random.randint(0,3)]
        self.flag=False if self.flag else True
        # self.sendMessage(json.dumps({ "command": "rotation", "player": { "connid": self.playerID, "angle": self.r } }))
        reactor.callLater(5, self.rtang)

    def movetank(self):
        if self.flag:
            self.x+=2
        else:
            self.y+=2 
        # self.sendMessage(json.dumps({ "command": "rotation", "player": { "connid": self.playerID, "angle": self.r } }))            
        self.sendMessage(json.dumps( {"command":"move","player": {"pos":{"y":self.y,"x":self.x},"connid": self.playerID}}))
        reactor.callLater(0.1, self.movetank)
        # {"command":"move","player": {"pos":{"y":500,"x":250},"connid": 1}}        
   
    


if __name__ == '__main__':

    log.startLogging(sys.stdout)
    timespeed = 0.5
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",
                      help="The WebSocket URL", default="wss://118.25.46.180:9000") 
    # parser.add_option("-u", "--url", dest="url",
    #                   help="The WebSocket URL", default="wss://127.0.0.1:9000")#wss://118.25.46.18:9000
    parser.add_option("-c", "--creat", dest="creat",
                      help="init_room,join_room", default="init_room")
    parser.add_option("-p", "--pid", dest="pid", help="pid", default=1)
    parser.add_option("-r", "--room", dest="room", help="roomid", default=88888888)

    (options, args) = parser.parse_args()

    # create a WS server factory with our protocol
    ##
    factory = WebSocketClientFactory(options.url)
    factory.protocol = EchoClientProtocol

    # SSL client context: default
    ##
    if factory.isSecure:
        contextFactory = ssl.ClientContextFactory()
    else:
        contextFactory = None

    connectWS(factory, contextFactory)
   
    with open("./pid",'a') as file:
        pid=os.getpid()        
        file.writelines(str(pid)+'\n')
    reactor.run()

