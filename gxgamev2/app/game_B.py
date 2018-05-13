# coding:utf8
from twisted.python import log
import random
import app.split 


class Gamemanger_B(object):
    rooms = {}


    @classmethod
    def getroomid(self):
        self._roomid= random.randint(10000000,99999999)
        if self._roomid in self.rooms or self._roomid in [66666666,88888888]:
            return None
        else:    
            self.rooms[self._roomid]=self._roomid
            return self._roomid

    def init_room(self,kw):
        print kw,"initroom"
        _room=mjroom(kw['data']['roomid'],kw['data']['pid'])
        if _room.roomid in self.rooms:
            raise Exception("System roomid conflict")
        self.rooms[kw['data']['roomid']]=_room
        _room.initplayer(kw['data'],kw['conn'])
        pass

    def join_room(self, kw):
        print kw,"joinroom"
        if kw['data']['roomid'] in self.rooms:
            room = self.rooms[kw['data']['roomid']]
            room.initplayer(kw['data'],kw['conn'])
        pass        
    
    def ready(self, kw):
        print "ready",kw
        room = self.rooms[kw['data']['roomid']]
        room.readygame(kw['data'])

    def switch(self, **kw):
        return {
            'init_room': self.init_room,
            'join_room':self.join_room,
            'ready':self.ready,
        }[kw["data"]["command"]](kw)     

    # def handledata(self, json_data):
    #     d = Deferred()
    #     try:
    #         self.switch(json_data)
    #     except TypeError as e:
    #         pass
    #         # log.err(str(e))
    #     d.addCallback(self.actions)
    #     d.callback(json_data)
    #     return d


class mjroom(object):
    
    def __init__(self,roomid,roomroot):
        self.roomroot = roomroot
        self.roomid= roomid
        self.players={}
        self.cards=None
 

    def initplayer(self, data,conn):
        print data,"initplayer"
        _play=player(data['pid'],conn)
        if len(self.players) > 4:
            raise Exception("player ge 4")
        self.players[_play.pid]=_play

    def readygame(self,data):
        print data
        readyok=0
        for p in self.players.values():
            if data['pid']==p.pid:
                p.readystat=data['readystat']
            readyok+=p.readystat
        print readyok
        if readyok==4:
            print 'statgame'
            self.startgame()
            pass
        
    def startgame(self):
        self.cards=[i for i in xrange(34) for j in xrange(4)]
        for p in self.players.values():
            for i in xrange(14):
                try:
                    j = self.cards.pop(random.randint(0, len(self.cards)-1))
                    p.handcard[j] = p.handcard[j] + 1
                except IndexError as e:
                    print '########',e
            print p.handcard
            print self.cards
        pass        


        

class player(object):
    def __init__(self,pid,conn,readystat=0):  #{readestat 0:没准备，1：准备}
        self.pid = pid
        self.roomid= conn
        self.readystat= readystat
        self.handcard=[0 for i in xrange(34)]



#{8888:obj.play}        