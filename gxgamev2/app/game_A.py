# coding:utf8
from twisted.python import log
from twisted.internet import reactor
import json
import time
import random
from twisted.internet.defer import Deferred, DeferredList, gatherResults, returnValue


class Gamemanger(object):
    clients = {}

    def __init__(self):
        self.tickcount = 0

    def unregister(self, client):
        try:
            del self.clients[client]
        except Exception as e:
            log.msg('unregister',str(e))

    def register(self, json_data, connid):
        print "register"
        _ps = pople(json_data["name"], connid,
                    json_data["x"], json_data["y"], json_data["playerType"], json_data["angle"],random.randint(1,3))
        if _ps.connid in self.clients:
            raise Exception("System record conflict")
        self.clients[_ps.connid] = _ps
        pl, selfplayers = self.getallpopleinfo("init")
        _ps.playerType = 2
        xx, players = self.getpopleinfobyconnid("init", _ps.connid)
        return pl, players, selfplayers

    def getallpopleinfo(self, command):
        _data = []
        for p in self.clients.values():
            _data.append({"connid": p.connid, 'team': 0, 'tankType': p.tankType, 'playerID': p.connid,
                          "playerType": p.playerType, "angle": p.angle, "pos": {"x": p.x, "y": p.y}, "name": p.name})
        return self.clients.keys(), {"command": command, "players": _data}

    def movebroad(self, command):
        for p in self.clients.values():
            _data=None
            if p.movestat :
                _data={"connid": p.connid, 'team': 0, 'tankType': p.tankType, 'playerID': p.connid,
                            "playerType": p.playerType, "angle": p.angle, "pos": {"x": p.x, "y": p.y}, "name": p.name}
                p.movestat =False                            
            yield self.clients.keys(), {"command": command, "player": _data}


    def getpopleinfobyconnid(self, command, connid):
        _data = []
        p = self.clients.get(connid, None)
        _data.append({"connid": p.connid, 'team': 0, 'tankType': p.tankType, 'playerID': p.connid,
                      "playerType": 2, "angle": p.angle, "pos": {"x": p.x, "y": p.y}, "name": p.name})
        return self.clients.keys(), {"command": command, "players": _data}

    def actions(self, json_data):
        if json_data['command'] == "move":
            pass
        else:
            p = self.clients.get(json_data['player']['connid'], None)
            _data = {"connid": p.connid, 'team': 0, 'tankType': p.tankType, 'playerID': p.connid,
                    'playerType': 1, "angle": p.angle, "pos": {"x": p.x, "y": p.y}, "name": p.name}
            return self.clients.keys(), {"command": json_data['command'], "player": _data}

    def _move(self, json_data):
        p = self.clients.get(json_data["player"]["connid"], None)
        p.x = json_data.get('player').get("pos").get("x")
        p.y = json_data.get('player').get("pos").get("y")
        p.movestat = True
        # return p

    def _rotation(self, json_data):
        p = self.clients.get(json_data["player"]["connid"], None)
        p.angle = json_data.get('player').get('angle')
        # return p

    def _gameover(self,json):
        reactor.callLater(1, self.unregister,json["player"]["connid"])       

    def switch(self, json_data):
        return {
            'move': self._move,
            'rotation': self._rotation,
            'attack': None,
            'gameover': self._gameover,
            'kill':self._gameover
        }[json_data["command"]](json_data)

    def handledata(self, json_data):
        d = Deferred()
        try:
            self.switch(json_data)
        except TypeError as e:
            pass
            # log.err(str(e))
        d.addCallback(self.actions)
        d.callback(json_data)
        return d


class pople(object):
    def __init__(self, name, connid, x, y, playerType, angle,tankType):
        self.connid = connid
        self.name = name
        self.x = x
        self.y = y
        self.playerType = playerType
        self.angle = angle
        self.movestat = False
        self.tankType = tankType
        
