# coding:utf8
from twisted.python import log
from twisted.internet import reactor
import json
import time
import random
from twisted.internet.defer import Deferred, DeferredList


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
                          "name": p.name, "jineng": "qwer", "action": 'move'})
            _cid.append(p.connid)
        return _cid, {"status": 0, "command": "play", "data": _data}

    def handledata(self, json_data):
        deferred_move = Deferred()
        deferred_jineng = Deferred()

        # Pack them into a DeferredList
        dl = DeferredList([deferred_move,deferred_jineng], consumeErrors=True)

        # Add our callback
        dl.addCallback(self.gogo)
        # Fire our three deferreds with various values.
        reactor.callLater(10, deferred_move.callback,"move")
        reactor.callLater(5, deferred_jineng.callback,"jineng")
        
        # deferred_move.callback(json_data["data"][0])
        return deferred_move

    def gogo(self, json_data):
        print '################'
        # time.sleep(15)
        print json_data
           


class pople(object):
    def __init__(self, name, connid, x, y, jineng=''):
        self.connid = connid
        self.name = name
        self.x = x
        self.y = y
        self.jineng = jineng


