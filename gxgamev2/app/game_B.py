# coding:utf8
from twisted.python import log
import random


class Gamemanger_B(object):
    rooms = {}


    @classmethod
    # @property
    def getroomid(self):
        self._roomid= random.randint(10000000,99999999)
        if self._roomid in self.rooms or self._roomid in [66666666,88888888]:
            return None
        else:    
            self.rooms[self._roomid]=self._roomid
            return self._roomid

    def init_room(self, roomid,roomroot):
        _room=mjroom(roomid,roomroot)
        if _room.roomid in self.rooms:
            raise Exception("System record conflict")
        self.rooms[roomid]=_room
        pass

    def join_room(self, connid):
        pass        

    def test(self):
        print "test ok"        

    pass


class mjroom(object):
    
    def __init__(self,roomid,roomroot):
        self.roomroot = roomroot
        self.roomid= roomid
        self.player1={'connid':None,'conn':None,'readstat':1}
        self.player2={'connid':None,'conn':None,'readstat':1}
        self.player3={'connid':None,'conn':None,'readstat':1}
        self.player4={'connid':None,'conn':None,'readstat':1}

    def readgame(self,data):
        
        pass
        

    

class player(object):
    def __init__(self,connid,conn,readstat=1):  #{readestat 1:没准备，0：准备}
        self.connid = connid
        self.roomid= conn
        self.readestat= readstat
        self.handcard=[]



#{8888:obj.play}        