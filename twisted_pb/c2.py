#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from __future__ import print_function

from twisted.spread import pb
from twisted.internet import reactor


def main():
    factory = pb.PBClientFactory()
    reactor.connectTCP("localhost", 8800, factory)
    def1 = factory.getRootObject()
    def1.addCallback(got_obj) # hands our 'two' to the callback
    reactor.run()

def got_obj(obj):
    cc=obj.callRemote("callTarget", "gate","print")
    cc.addCallback(lambda a: print(a))
    cc.addCallback(lambda a: reactor.stop())


main()