# coding:utf8
from twisted.python import log
from twisted.internet import reactor
import json


class Gamemanger(object):
    clients = {}

    def __init__(self):
        self.tickcount = 0

    def unregister(self, client):
        try:
            del self.clients[client]
        except Exception as e:
            log.msg(str(e))

    def register(self, json_data):
        print "register"
        _ps = pople(json_data["name"], json_data["x"],
                    json_data["y"], json_data["connid"])
        if _ps.connid in self.clients:
            raise Exception("系统记录冲突")
        self.clients[_ps.connid] = _ps

    def getallpopleinfo(self):
        _data = []
        _cid = []
        for p in self.clients.values():
            _data.append({"connid": p.connid, "x": p.x, "y": p.y,"name":p.name})
            _cid.append(p.connid)
        return _cid, {"data": _data}

    def handledata(self, json_data):
        print "handle"
        self.register(json_data)


class pople(object):
    def __init__(self, name, x, y, connid):
        self.connid = connid
        self.name = name
        self.x = x
        self.y = y
