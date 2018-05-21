# coding:utf8
from twisted.python import log
import random
import app.split 
import json
from app.models.users_models import User, WXUser
from app import db


class Gamemanger_B(object):
    rooms = {}
    @classmethod
    def getroomid(self):
        self._roomid= random.randint(10000000,99999999)
        if self._roomid in self.rooms or self._roomid in [66666666,88888888]:
            return None
        else:    
            return self._roomid

    @classmethod
    def getroomstatus(self,roomid):
        print roomid
        if not roomid in self.rooms:
            return  1,'roomid wuxiao'
        elif len(self.rooms[roomid].players)==4:
            return  1,'player full'
        else:
            return 0,roomid            
                   
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
        else:
            kw['conn'].sendMessage(json.dumps({"error":'wuxiao roomid'}).encode('utf8'))  
            
    def overroom(self, kw):
        print kw,"overroom"
        if kw['data']['roomid'] in self.rooms:
            room = self.rooms[kw['data']['roomid']]
            if room.roomroot==kw['data']['pid']:
                us = WXUser.query.filter_by(id=kw['data']['pid']).first()
                us.roomid=None  
                db.session.commit() 
                for p in room.players.values():
                    p.conn.dropConnection(abort=True)
                del self.rooms[kw['data']['roomid']]
    
    def ready(self, kw):
        print "ready",kw
        room = self.rooms[kw['data']['roomid']]
        room.readygame(kw['data'])

    def outcard(self, kw):
        print "outcard",kw
        room = self.rooms[kw['data']['roomid']]
        room.outcardgame(kw['data']['pid'],kw['data']['outcard'])


    def switch(self, **kw):
        return {
            'init_room': self.init_room,
            'join_room':self.join_room,
            'ready':self.ready,
            'outcard': self.outcard,
            'overroom': self.overroom
        }[kw["data"]["command"]](kw)     



class mjroom(object):
    
    def __init__(self,roomid,roomroot):
        self.roomroot = roomroot
        self.roomid= roomid
        self.players={}
        self.cards=None
        self.banker=roomroot
        self.guicard=None
        self.roomonly=[1,2]
        
 
        
    def initplayer(self, data,conn):
        print data,"initplayer"
        if len(self.players) == 4:
            raise Exception("player ge 4")  
        if data['pid'] in self.players:   #断线
            oldp=self.players.get(data['pid'])
            oldp.conn.dropConnection(abort=True)
            oldp.conn=conn
        else:
            _play=player(data['pid'],conn,onlyone=self.roomonly.pop(random.randint(0,len(self.roomonly)-1)))
            self.players[_play.pid]=_play
            self.broadcast({"command":data['command'],"pinfo":[_play.pinfo()]},[_play.pid])
            _play.conn.sendMessage( json.dumps({"command":data['command'],"pinfo":[p.pinfo() for p in self.players.values()]}))

    def readygame(self,data):
        print data
        readyok=0
        for p in self.players.values():
            if data['pid']==p.pid:
                p.readystat=data['readystat']
                self.broadcast({"command":data['command'],"roomid":self.roomid,"pinfo":p.pinfo()})
            readyok+=p.readystat
        print readyok
        if readyok==2:  #准备状态
            self.broadcast({"command":"startgame"})
            self.startgame()

    def broadcast(self, msg,passpid=None):
        for p in self.players.values():
            if passpid is None:
                p.conn.sendMessage(json.dumps(msg))  
            elif p.pid in passpid:
                pass
            else:
                p.conn.sendMessage(json.dumps(msg))                     
        
    def startgame(self):
        self.guicard=(random.randint(1,33))
        print 'guicard',self.guicard
        self.cards=[i for i in xrange(34) for j in xrange(4)]
        for p in self.players.values():              
            for i in xrange(13):
                try:
                    j = self.cards.pop(random.randint(0, len(self.cards)-1))
                    p.handcard[j] = p.handcard[j] + 1
                except IndexError as e:
                    print '########',e
            p.conn.sendMessage(json.dumps({"command":"gaming","pinfo":p.pinfo(["conn"])}))
            if self.banker==p.pid:
                self.getcard(p)

    def getcard(self,p):
        try:
            j = self.cards.pop(random.randint(0, len(self.cards)-1))
            p.conn.sendMessage(json.dumps({"command":"getcard","pinfo":p.pinfo(),"getcard":j}))
            p.handcard[j] = p.handcard[j] + 1
            if app.split.get_hu_info(p.handcard, 34, self.guicard):
                print 'send zimohule'
        except IndexError as e:
            print '########',e

    def outcardgame(self, pid,j):
        for p in self.players.values():
            if pid ==p.pid:
                print 'nowout',p.handcard
                p.handcard[j] = p.handcard[j] - 1
                pre_p=p.onlyone
                print 'nowout',p.handcard
                continue
            print p.handcard                                
            tmpcards=p.handcard[:]
            tmpcards[j]=tmpcards[j]+1
            print tmpcards
            try:
                if app.split.get_hu_info(tmpcards, 34, self.guicard):
                    print 'send zimohule'            
                    break
                else:
                    print  "cat't hu" ,p.pid
            except Exception as e:
                print "huerror", e
        nextout_p=self._nextoutcard(pre_p)  
        # print nextout_p.info()
        try:
            j = self.cards.pop(random.randint(0, len(self.cards)-1))
            nextout_p.conn.sendMessage(json.dumps({"command":"getcard","pinfo":nextout_p.pinfo(),"getcard":j}))
            nextout_p.handcard[j] = nextout_p.handcard[j] + 1
            if app.split.get_hu_info(nextout_p.handcard, 34, self.guicard):
                print 'send zimohule'
        except IndexError as e:
            print '########',e         
             

    def _nextoutcard(self, pre):
        c=pre%2+1
        for p in self.players.values():
            if c==p.onlyone:                          
                return p
    

class player(object):
    def __init__(self,pid,conn,readystat=0,onlyone=-1):  #{readestat 0:没准备，1：准备}
        self.pid = pid
        self.conn= conn
        self.readystat= readystat
        self.handcard=[0 for i in xrange(34)]
        self.onlyone=onlyone


    def pinfo(self,items=None):
        info={}
        if items==None:
            items=["conn","handcard"]
        for key in self.__dict__:
            if key in items:
                pass
            else:
                info[key]=self.__dict__[key]          
        return info            

    