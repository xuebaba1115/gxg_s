#coding:utf8
"""
Created on 2011-10-14
分布式根节点
@author: lan (www.9miao.com)
"""
from twisted.python import log
from twisted.spread import pb
import random

class BilateralBroker(pb.Broker):

    def connectionLost(self, reason):
        clientID = self.transport.sessionno
        log.msg("node [%d] lose"%clientID)
        pb.Broker.connectionLost(self, reason)

class BilateralFactory(pb.PBServerFactory):

    protocol = BilateralBroker


class PBRoot(pb.Root):
    """PB 协议"""

    def __init__(self,serviceName):
        """初始化根节点
        """
        pb.Root()
        self.child={}

    def addServiceChannel(self,service):
        self.service = service

    def remote_register(self,name,peer):
        log.msg('node [%s] registered' % name)
        print name,peer
        cclass=self.child.get(name)
        if not cclass:
            self.child[name]=[peer]            
        else:
            cclass.append(peer)
        print self.child            

    def remote_callTarget(self,name,*args,**kw):
        ch=self.child.get(name)
        if ch:
            witchone=ch[random.randint(0,len(ch)-1)]
            data = witchone.callRemote(*args,**kw)
            return data


