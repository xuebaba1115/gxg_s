#coding:utf8
"""
Created on 2011-10-14
分布式根节点
@author: lan (www.9miao.com)
"""
from twisted.python import log
from twisted.spread import pb





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
        """添加服务通道
        @param service: Service Object(In bilateral.services)
        """
        self.service = service

    def remote_register(self,name,peer):
        """设置代理通道
        @param addr: (hostname,port)hostname 根节点的主机名,根节点的端口
        """
        log.msg('node [%s] registered' % name)
        print name,peer
        # self.childsmanager.addChildByNamePeer(name,peer)
        self.child[name]=peer
        

    def remote_callTarget(self,name,*args,**kw):
        ch=self.child.get(name)
        if ch:
            data = ch.callRemote('print',*args,**kw)
            return data


