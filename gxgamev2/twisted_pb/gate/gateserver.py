
from twisted.python import log
from twisted.internet import reactor


from root import PBRoot,BilateralFactory
# from leafnode import leafNode
from globalobject import GlobalObject
import os
import sys



class gateserver:
    
    def __init__(self):
        self.root=None
        self.servername=None

    def config(self):
        self.servername='gate'
        self.root = PBRoot("rootservice")
        reactor.listenTCP(8800, BilateralFactory(self.root))
        GlobalObject().root = self.root

    def start(self):   
        reactor.run()


    

if __name__ == '__main__':
    ser=gateserver()
    ser.config()
    ser.start()