# coding:utf8
from twisted.python import log
from twisted.internet import reactor
import json
import time
import random
from twisted.internet.defer import Deferred, DeferredList,gatherResults


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
        _ps = pople(json_data["name"], json_data["connid"],
                    json_data["x"], json_data["y"])
        if _ps.connid in self.clients:
            raise Exception("System record conflict")
        self.clients[_ps.connid] = _ps

    def getallpopleinfo(self):
        _data = []
        _cid = []
        for p in self.clients.values():
            _data.append({"connid": p.connid, "x": p.x, "y": p.y,
                          "name": p.name, "jineng": p.jineng, "action": 'move'})
            _cid.append(p.connid)
        return _cid, {"status": 0, "command": "play", "data": _data}

    def handledata(self, json_data):
        # d = Deferred()
        p=self.clients.get(json_data["data"][0]["connid"],None)
        p.x=json_data["data"][0]["x"]
        p.y=json_data["data"][0]["y"]
        p.jineng=json_data["data"][0]["jineng"]
        # d.callback(None)
        return None



class pople(object):
    def __init__(self, name, connid, x, y, jineng=None):
        self.connid = connid
        self.name = name
        self.x = x
        self.y = y
        self.jineng = jineng


