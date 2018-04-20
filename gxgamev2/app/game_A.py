# coding:utf8
from twisted.internet import reactor
import json


class Gamemanger(object):
    clients = []
    _pss = []

    def __init__(self):
        self.tickcount = 0

    def register(self, client):
        if client not in self.clients:
            print("registered client ")
            self.clients.append(client)
            print self.clients

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client ")
            self.clients.remove(client)

    def initpople(self, json_data):
        print "initpople"
        _ps = pople(json_data["name"], json_data["x"],
                         json_data["y"], json_data["connid"])
        if _ps in self._pss:
            raise Exception("系统记录冲突")
        self._pss.append(_ps)     
        print self._pss                             

    def getallpopleinfo(self):
        _data=[]
        for p in self._pss:
            _data.append({"connid":p.connid,"x":p.x,"y":p.y})
        return self.clients,{"data":_data}            
            # p.connid
            # p.name
            # p.x
            # p.y
            

    def handledata(self, json_data):
        print json_data["command"]
        print json_data["connid"]
        self.register(json_data["connid"])
        self.initpople(json_data)


class pople(object):
    def __init__(self, name, x, y, connid):
        self.connid = connid
        self.name = name
        self.x = x
        self.y = y
