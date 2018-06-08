#coding:utf8

from singleton import Singleton

class GlobalObject:

    __metaclass__ = Singleton

    def __init__(self):
        self.netfactory = None#net前端
        self.root = None#分布式root节点
        self.remote = {}#remote节点

