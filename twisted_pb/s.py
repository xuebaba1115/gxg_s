#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from __future__ import print_function

from twisted.spread import pb
from twisted.internet import reactor
from twisted.python import log
        
class One(pb.Root):

    def __init__(self):
        self.child={}

    def remote_takeTwo(self, two):
        print("received a Two called", two)
        print("telling it to print(12)")
        two.callRemote("print", 12)

    def remote_register(self,name,peer):

        log.msg('node [%s] registered' % name)
        # self.childsmanager.addChildByNamePeer(name,peer)        
        self.child[name]=peer            

reactor.listenTCP(8800, pb.PBServerFactory(One()))
reactor.run()
