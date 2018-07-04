
import sys,json
import random
from optparse import OptionParser

from twisted.python import log
from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS


class EchoClientProtocol(WebSocketClientProtocol):
    onlyone=None
    handcards=None
    def onOpen(self):
        self.sendMessage(json.dumps({"command":options.creat,"roomid":88888888,"pid":options.pid}))
        pass

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                x = json.loads(payload.decode('utf8'))
                print x
                self.analysis(x)
            except Exception as e:
                self.sendMessage(json.dumps(
                    {"errcode": 1, "errmsg": "%s" % e}).encode('utf8'))

    def analysis(self,x):
        if x['command']==options.creat:
            for i in  x['pinfo']:
                if i['pid']==options.pid:
                    self.onlyone=i['onlyone']
            print self.onlyone
            self.sendMessage(json.dumps({"command":"ready","roomid":88888888,"readystat":1,"pid":options.pid}))
        if x['command']=='gaming':
            for i in  x['pinfo']:
                if i=='handcard':
                    self.handcards=x['pinfo'][i]
        if x['command']== 'getcard':
            reactor.callLater(5,self.sendMessage,json.dumps({"command":"outcard","roomid":88888888,"pid":options.pid,"outcard":x['getcard'],"pre_p":self.onlyone}))

        if x['command']=='gpch':   
            print '#####gpche',self.handcards
            sjcard=self.suijicard()    
            print sjcard
            for i in x['c_action']  :
                print i
                if i=='peng':
                    reactor.callLater(5,self.sendMessage,json.dumps({"command":"peng","roomid":88888888,"pid":options.pid,"pengcard":x['indexcard'],"pre_p":x['ppre']}))
                    reactor.callLater(6,self.sendMessage,json.dumps({"command":"outcard","roomid":88888888,"pid":options.pid,"outcard":sjcard,"pre_p":self.onlyone}))
                    break

                if i=='chi':
                    for clist in x['chicard']:
                        print clist
                        reactor.callLater(5,self.sendMessage,json.dumps({"command":"chi","roomid":88888888,"pid":options.pid,"chicard":x['indexcard'],"chilist":clist}))
                        reactor.callLater(6,self.sendMessage,json.dumps({"command":"outcard","roomid":88888888,"pid":options.pid,"outcard":sjcard,"pre_p":self.onlyone}))
                        break
                if i=='hu':
                    print 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh'
                    reactor.stop()                        

    def suijicard(self):
        while 1:
            delid=random.randint(0,len(self.handcards)-1)
            if self.handcards[delid] >0: 
                self.handcards[delid]=self.handcards[delid]-1
                break
        return delid
        

if __name__ == '__main__':

    log.startLogging(sys.stdout)

    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url", help="The WebSocket URL",default="wss://192.168.1.16:9000")
    parser.add_option("-c", "--creat", dest="creat", help="init_room,join_room",default="init_room")
    parser.add_option("-p", "--pid", dest="pid", help="pid",default=1)
    
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
    reactor.run()