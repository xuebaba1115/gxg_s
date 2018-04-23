# coding:utf8
from twisted.python import log
from twisted.internet import reactor
import json
import time
import random
from twisted.internet.defer import Deferred,DeferredList


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
            raise Exception("System record conflict")
        self.clients[_ps.connid] = _ps

    def getallpopleinfo(self):
        _data = []
        _cid = []
        for p in self.clients.values():
            _data.append({"connid": p.connid, "x": p.x, "y": p.y,"name":p.name,"action":'move or chat'})
            _cid.append(p.connid)
        return _cid, {"status":0,"command":"play","data": _data}


    def handledata(self, json_data):
        d = Deferred()
        d.addCallback(self.register)
        d.callback(json_data)
        # reactor.callLater(random.randint(5, 12), d.callback, json_data)
        return d


# deferred_move = defer.Deferred()
# deferred_chat = defer.Deferred()
# deferred_gongji = defer.Deferred()

# # Pack them into a DeferredList
# dl = defer.DeferredList([deferred_move, deferred_chat, deferred_gongji], consumeErrors=True)

# # Add our callback
# dl.addCallback(printResult)

# # Fire our three deferreds with various values.
# deferred1.callback('one')
# deferred2.errback(Exception('bang!'))
# deferred3.callback('three')
    
         


class pople(object):
    def __init__(self, name, x, y, connid):
        self.connid = connid
        self.name = name
        self.x = x
        self.y = y
