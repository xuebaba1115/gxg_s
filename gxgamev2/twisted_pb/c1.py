#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from __future__ import print_function

from twisted.spread import pb
from twisted.internet import reactor

def callBack(obj,funcName,*args,**kw):

    return obj.callRemote(funcName, *args,**kw)

class Two(pb.Referenceable):
    a=1000
    b=100
    def remote_print(self):
        print("Two.print() called with")
        c=self.a*self.b
        print (c)
        return c

    def callRemote(self,commandId,*args,**kw):
        c=self.a*self.b
        print (c)
        return c
        # deferedRemote = self._factory.getRootObject()
        # return deferedRemote.addCallback(callBack,'callTarget',commandId,*args,**kw)            
    
        

def main():
    two = Two()
    factory = pb.PBClientFactory()
    reactor.connectTCP("localhost", 8800, factory)
    def1 = factory.getRootObject()
    def1.addCallback(got_obj, two) # hands our 'two' to the callback
    reactor.run()

def got_obj(obj, two):
    obj.callRemote("register", "gate",two)

main()