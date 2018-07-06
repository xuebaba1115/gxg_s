
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
    onlyone = None
    handcards = None
    root=False
    def onOpen(self):
        self.sendMessage(json.dumps(
            {"command": options.creat, "roomid": options.room, "pid": options.pid}))
        pass

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                x = json.loads(payload.decode('utf8'))
                self.analysis(x)
            except Exception as e:
                self.sendMessage(json.dumps(
                    {"errcode": 1, "errmsg": "%s" % e}).encode('utf8'))

    def analysis(self, x):
        if x['command'] == options.creat and self.onlyone == None:
            if x['command']=='init_room':
                self.root=True
            for i in x['pinfo']:
                if i['pid'] == options.pid:
                    self.onlyone = i['onlyone']
            print 'pid:', options.pid, 'onlyone:', self.onlyone
            self.sendMessage(json.dumps(
                {"command": "ready", "roomid": options.room, "readystat": 1, "pid": options.pid}))

        if x['command'] == 'gaming':
            for i in x['pinfo']:
                if i == 'handcard':
                    self.handcards = x['pinfo'][i]
            self.handcards[x['guicard']] = 0
            print '##guicard', x['guicard']

        if x['command'] == 'getcard':
            time.sleep(timespeed)
            print '##get_card,outcard', x['getcard']
            self.sendMessage(json.dumps({"command": "outcard", "roomid": options.room,
                                         "pid": options.pid, "outcard": x['getcard'], "pre_p": self.onlyone}))

        if x['command'] == 'gpch':
            for i in x['c_action']:
                print '##get_gpch', i, x['indexcard']
                if i == 'hu':
                    self.sendMessage(json.dumps({"command":"hu", "roomid": options.room,"hucard":x['indexcard'],"pid":options.pid}))
                    print 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh'
                    reactor.callLater(1,reactor.stop)

                if i == 'minggang_peng':
                    time.sleep(timespeed)
                    self.handcards[x['indexcard']
                                   ] = self.handcards[x['indexcard']] - 3
                    sjcard = self.suijicard()
                    self.sendMessage(json.dumps(
                        {"command": "gang", "roomid": options.room, "pid": options.pid, "gangcard": x['indexcard'], "pre_p": x['ppre']}))
                    time.sleep(timespeed)
                    self.sendMessage(json.dumps(
                        {"command": "outcard", "roomid": options.room, "pid": options.pid, "outcard": sjcard, "pre_p": self.onlyone}))
                    print 'minggang', sjcard

                if i == 'peng':
                    self.handcards[x['indexcard']
                                   ] = self.handcards[x['indexcard']] - 2
                    sjcard = self.suijicard()
                    time.sleep(timespeed)
                    self.sendMessage(json.dumps(
                        {"command": "peng", "roomid": options.room, "pid": options.pid, "pengcard": x['indexcard'], "pre_p": x['ppre']}))
                    time.sleep(timespeed)
                    self.sendMessage(json.dumps(
                        {"command": "outcard", "roomid": options.room, "pid": options.pid, "outcard": sjcard, "pre_p": self.onlyone}))
                    print '##peng out', sjcard
                    break

                if i == 'chi':
                    for clist in x['chicard']:
                        print clist
                        self.handcards[clist[1]] = self.handcards[clist[1]] - 1
                        self.handcards[clist[2]] = self.handcards[clist[2]] - 1
                        sjcard = self.suijicard()
                        time.sleep(timespeed)
                        self.sendMessage(json.dumps(
                            {"command": "chi", "roomid": options.room, "pid": options.pid, "chicard": x['indexcard'], "chilist": clist}))
                        time.sleep(timespeed)
                        self.sendMessage(json.dumps(
                            {"command": "outcard", "roomid": options.room, "pid": options.pid, "outcard": sjcard, "pre_p": self.onlyone}))
                        print '##chi out', sjcard
                        break

        if x['command'] == 'other_hu':
            if self.root:
                self.sendMessage(json.dumps({"command":"overroom","roomid":options.room,"pid":options.pid}))  
                reactor.callLater(1,reactor.stop)
            else:
                reactor.callLater(1,reactor.stop)

        if x['command'] == 'nocard' :       
            print 'nocard######################'
            time.sleep(timespeed+2)
            self.handcards = None
            self.sendMessage(json.dumps(
                {"command": "ready", "roomid": options.room, "readystat": 1, "pid": options.pid}))            
               
                                                                                  

    def suijicard(self):
        while 1:
            delid = random.randint(0, len(self.handcards) - 1)
            if self.handcards[delid] > 0:
                self.handcards[delid] = self.handcards[delid] - 1
                break
        print filter(lambda l: l > 0, self.handcards)
        return delid


if __name__ == '__main__':

    log.startLogging(sys.stdout)
    timespeed = 0.5
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",
                      help="The WebSocket URL", default="wss://118.25.46.180:9000") #wss://118.25.46.18:9000
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
