# coding:utf8
from twisted.python import log
from twisted.internet import reactor
import json
import time
import random
from twisted.internet.defer import Deferred, DeferredList, gatherResults,returnValue


class Gamemanger(object):
    clients = {}

    def __init__(self):
        self.tickcount = 0

    def unregister(self, client):
        try:
            del self.clients[client]
        except Exception as e:
            log.msg(str(e))

    def register(self, json_data, connid):                           
        print "register"
        _ps = pople(json_data["name"], connid,
                    json_data["x"], json_data["y"])
        if _ps.connid in self.clients:
            raise Exception("System record conflict")
        self.clients[_ps.connid] = _ps
        pl, players = self.getallpopleinfo("init")
        return pl,players

    def getallpopleinfo(self,command):
        _data = []
        _cid = []
        for p in self.clients.values():
            _data.append({"connid": p.connid, 'team': 0, 'tankType': 1, 'playerID': p.connid,
                          'playerType': 1, "pos": {"x": p.x, "y": p.y}, "name": p.name})
            _cid.append(p.connid)
        return _cid, {"command": command, "players": _data}

    def actions(self, json_data):
        p = self.clients.get(json_data['player']['connid'],None)
        _data =  {"connid": p.connid, 'team': 0, 'tankType': 1, 'playerID': p.connid,'playerType': 1, "pos": {"x": p.x, "y": p.y}, "name": p.name}
        return self.clients.keys(),{"command": json_data['command'], "player": _data}

    def handledata(self, json_data):
        d = Deferred()
        p = self.clients.get(json_data["player"]["connid"], None)
        p.x = json_data["player"]["pos"]["x"]
        p.y = json_data["player"]["pos"]["y"]
        d.addCallback(self.actions)
        d.callback(json_data)
        return d


class pople(object):
    def __init__(self, name, connid, x, y):
        self.connid = connid
        self.name = name
        self.x = x
        self.y = y
