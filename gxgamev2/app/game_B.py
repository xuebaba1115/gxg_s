# coding:utf8
from twisted.python import log


class Gamemanger_B(object):
    rooms = {}

    # def __init__(self):
    #     self.tickcount = 0

    def create_room(self, roomid,connroot):
        _room=mjroom(roomid,connroot)
        if _room.roomid in self.rooms:
            raise Exception("System record conflict")
        self.rooms[roomid]=_room
        pass

    def test(self):
        print "test ok"        

    pass


class mjroom(object):
    
    def __init__(self,roomid,connroot):
        self.connroot = connroot
        self.roomid= roomid
        