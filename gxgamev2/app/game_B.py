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
        self._roomid = random.randint(10000000, 99999999)
        if self._roomid in self.rooms or self._roomid in [66666666, 88888888]:
            return None
        else:
            return self._roomid

    @classmethod
    def getroomstatus(self, roomid):
        print roomid
        if not roomid in self.rooms:
            return 1, 'roomid wuxiao'
        elif len(self.rooms[roomid].players) == 4:
            return 1, 'player full'
        else:
            return 0, roomid

    def init_room(self, kw):
        print kw, "initroom"
        _room = mjroom(kw['data']['roomid'], kw['data']['pid'])
        if _room.roomid in self.rooms:
            raise Exception("System roomid conflict")
        self.rooms[kw['data']['roomid']] = _room
        _room.initplayer(kw['data'], kw['conn'])
        pass

    def join_room(self, kw):
        print kw, "joinroom"
        if kw['data']['roomid'] in self.rooms:
            room = self.rooms[kw['data']['roomid']]
            room.initplayer(kw['data'], kw['conn'])
        else:
            kw['conn'].sendMessage(json.dumps(
                {"error": 'wuxiao roomid'}).encode('utf8'))

    def overroom(self, kw):
        print kw, "overroom"
        if kw['data']['roomid'] in self.rooms:
            room = self.rooms[kw['data']['roomid']]
            if room.roomroot == kw['data']['pid']:
                us = WXUser.query.filter_by(id=kw['data']['pid']).first()
                us.roomid = None
                db.session.commit()
                for p in room.players.values():
                    p.conn.dropConnection(abort=True)                                    
                del self.rooms[kw['data']['roomid']]

    def ready(self, kw):
        print "ready", kw
        room = self.rooms[kw['data']['roomid']]
        room.readygame(kw['data'])

    def outcard(self, kw):
        print "outcard", kw
        room = self.rooms[kw['data']['roomid']]
        room.outcardgame(kw['data']['pid'], kw['data']
                         ['outcard'], kw['data']['pre_p'])

    def peng(self, kw):
        print "peng", kw
        room = self.rooms[kw['data']['roomid']]
        room.penggame(kw['data']['pid'], kw['data']
                      ['pengcard'], kw['data']['pre_p'])

    def gang(self, kw):
        print "gang", kw
        room = self.rooms[kw['data']['roomid']]
        room.ganggame(kw['data']['pid'], kw['data']
                      ['gangcard'], kw['data']['pre_p'])

    def chi(self, kw):
        print "chi", kw
        room = self.rooms[kw['data']['roomid']]
        room.chigame(kw['data']['pid'], kw['data']
                     ['chicard'], kw['data']['chilist'])

    def hu(self, kw):
        print "hu", kw
        room = self.rooms[kw['data']['roomid']]
        room.hugame(kw['data']['pid'],kw['data']['hucard'])

    def switch(self, **kw):
        return {
            'init_room': self.init_room,
            'join_room': self.join_room,
            'ready': self.ready,
            'outcard': self.outcard,
            'overroom': self.overroom,
            'peng': self.peng,
            'gang': self.gang,
            'chi': self.chi,
            'hu':self.hu
        }[kw["data"]["command"]](kw)


class mjroom(object):

    def __init__(self, roomid, roomroot):
        self.roomroot = roomroot
        self.roomid = roomid
        self.players = {}
        self.cards = None
        self.banker = roomroot
        self.guicard = None
        self.maxplayer = 4
        self.roomonly = range(1, self.maxplayer + 1)
        self.chicard = None
        self.cache_send = None

    def initplayer(self, data, conn):
        print data, "initplayer"
        if len(self.players) == self.maxplayer:
            raise Exception("player ge 4")
        if data['pid'] in self.players:  # 断线
            oldp = self.players.get(data['pid'])
            oldp.conn.dropConnection(abort=True)
            oldp.conn = conn
        else:
            _play = player(data['pid'], conn, onlyone=self.roomonly.pop(
                random.randint(0, len(self.roomonly) - 1)))
            self.players[_play.pid] = _play
            self.broadcast({"command": data['command'], "pinfo": [
                           _play.pinfo()]}, [_play.pid])
            _play.conn.sendMessage(json.dumps({"command": data['command'], "pinfo": [
                                   p.pinfo() for p in self.players.values()]}))

    def readygame(self, data):
        readyok = 0
        for p in self.players.values():
            if data['pid'] == p.pid:
                p.readystat = data['readystat']
                self.broadcast(
                    {"command": data['command'], "roomid": self.roomid, "pinfo": p.pinfo()})
            readyok += p.readystat
        if readyok == self.maxplayer:  # 准备状态
            self.broadcast({"command": "startgame"})
            self.startgame()

    def broadcast(self, msg, passpid=None):
        for p in self.players.values():
            if passpid is None:
                p.conn.sendMessage(json.dumps(msg))
            elif p.pid in passpid:
                pass
            else:
                p.conn.sendMessage(json.dumps(msg))

    def startgame(self):
        self.guicard = (random.randint(1, 33))
        print 'guicard', self.guicard
        self.cards = [i for i in xrange(34) for j in xrange(4)]
        for p in self.players.values():
            for i in xrange(13):
                try:
                    j = self.cards.pop(random.randint(0, len(self.cards) - 1))
                    p.handcard[j] = p.handcard[j] + 1
                except IndexError as e:
                    print '########s', e
            p.conn.sendMessage(json.dumps(
                {"command": "gaming", "pinfo": p.pinfo(["conn"]), "guicard": self.guicard}))     
            if int(self.banker) == int(p.pid):
                print '############################'
                self.getcard(p)

    def getcard(self, p):
        try:
            j = self.cards.pop(random.randint(0, len(self.cards) - 1))
            p.conn.sendMessage(json.dumps(
                {"command": "getcard", "pinfo": p.pinfo(), "getcard": j}))
            jieguo, _ = self.result_computer(p, j, p.onlyone)
            print '##Ganemgetstat##', jieguo
            p.handcard[j] = p.handcard[j] + 1
            if app.split.get_hu_info(p.handcard, 34, self.guicard):
                print 'send zimohule'
        except IndexError as e:
            print '########g', e

    def outcardgame(self, pid, j, pre_p):
        commdict = {}
        for p in self.players.values():
            if pid == p.pid:
                print 'nowout_qai', p.handcard
                p.handcard[j] = p.handcard[j] - 1
                print 'nowout_hou', p.handcard
                continue
            r_action, pp = self.result_computer(p, j, pre_p)
            if r_action:
                r_action.append(pp)
                commdict[pp.onlyone] = r_action

        if not commdict:
            self._nextoutcard(pre_p)
        else:
            print '##look', commdict, self.chicard
            # try:
            sortonly=[1,2,3,4]
            sortonly.append(sortonly.pop(pre_p-1))
            for i in sortonly:
                commlist = commdict.get(i)
                if commlist and not isinstance(self.cache_send,dict) :    
                    if 'hu' in commlist:
                            print 'sendchi'
                            commlist[-1].conn.sendMessage(json.dumps({"command": "gpch", "c_action": commlist[:-1], "indexcard": j, "chicard": self.chicard, "ppre": pre_p}))
                            self.chicard = None  
                            self.cache_send =None 
                            continue
                    if 'chi' in commlist:
                            print 'sendchi'
                            commlist[-1].conn.sendMessage(json.dumps({"command": "gpch", "c_action": commlist[:-1], "indexcard": j, "chicard": self.chicard, "ppre": pre_p}))
                            self.chicard = None  
                            self.cache_send =None 
                            continue
                    if 'minggang_peng' in commlist: 
                        print 'sendgang' 
                        commlist[-1].conn.sendMessage(json.dumps(
                            {"command": "gpch", "c_action": commlist[:-1], "indexcard": j, "ppre": pre_p}))
                        self.cache_send={}                             
                    if 'peng' in commlist: 
                        print 'sendpeng' 
                        commlist[-1].conn.sendMessage(json.dumps(
                            {"command": "gpch", "c_action": commlist[:-1], "indexcard": j, "ppre": pre_p}))
                        self.cache_send={}                                                                                                                           
                elif commlist and isinstance(self.cache_send,dict):
                    print 'other_peng,next_chi'
                    self.cache_send[i]=commlist
           

            # except Exception as e:
            #     print "##commaddiect##^^", e

    def result_computer(self, p, j, j_tag):
        c_action = []
        c = j_tag % self.maxplayer
        print 'soure card', p.onlyone, p.handcard
        tmpcards = p.handcard[:]
        tmpcards[j] = tmpcards[j] + 1
        print 'tmp   card', p.onlyone, tmpcards
        result_hu = app.split.get_hu_info(tmpcards, 34, self.guicard)
        result_peng = app.split.get_peng(j, p.handcard, p.pcg_list,self.guicard)
        result_gang = app.split.get_gang(j, p.handcard, p.pcg_list,self.guicard)
        if result_hu:
            c_action.append('hu')
        if result_peng and c != p.onlyone:
            c_action.append('peng')
        if result_gang == '+gang' and c == p.onlyone:
            c_action.append('+gang')
        elif result_gang == 'angang_peng' and c == p.onlyone:
            c_action.append('angang')
        elif result_gang == 'angang_peng':
            c_action.append('minggang_peng')
        if c + 1 == p.onlyone:
            self.chicard = app.split.chi(j, p.handcard, p.pcg_list,self.guicard)
            if self.chicard:
                c_action.append('chi')
        return c_action, p

    def penggame(self, pid, j, ppre):
        if j == 'guo' and not isinstance(self.cache_send,dict):
            self._nextoutcard(ppre)
            self.cache_send=None
        elif j=='guo' and isinstance(self.cache_send,dict):
            for i in self.cache_send.values():
                i[-1].conn.sendMessage(json.dumps(
                    {"command": "gpch", "c_action": i[:-1], "indexcard": j, "chicard": self.chicard, "pre_p": i[-1].onlyone}))   
            self.cache_send=None
            self.chicard=None                                 
        else:
            p = self.players.get(pid)
            p.handcard[j] = p.handcard[j] + 1
            p.pcg_list['peng'].append([j] * 3)
            self.broadcast(
                {"command": "other_peng", "pinfo": p.pinfo(), "indexcard": j}, passpid=[p.pid])
            self.cache_send=None
            self.chicard=None                  

    def hugame(self, pid,j):
        p = self.players.get(pid)
        self.broadcast(
            {"command": "other_hu", "pinfo": p.pinfo(), "indexcard": j}, passpid=[p.pid])        


    def ganggame(self, pid, j, ppre):
        if j == 'guo' and not isinstance(self.cache_send,dict):
            self._nextoutcard(ppre)
            self.cache_send=None
        elif j=='guo' and isinstance(self.cache_send,dict):
            for i in self.cache_send.values():
                i[-1].conn.sendMessage(json.dumps(
                    {"command": "gpch", "c_action": i[:-1], "indexcard": j, "chicard": self.chicard, "pre_p": i[-1].onlyone}))   
            self.cache_send=None
            self.chicard=None   
        else:
            p = self.players.get(pid)
            p.handcard[j] = p.handcard[j] + 1
            p.pcg_list['gang'].append([j] * 4)
            self.broadcast(
                {"command": "other_gang", "pinfo": p.pinfo(), "indexcard": j}, passpid=[p.pid])
            self.cache_send=None
            self.chicard=None                  

    def chigame(self, pid, j, jlist):
        p = self.players.get(pid)
        if j == 'guo':
            self._nextoutcard(p.onlyone - 1)
            self.cache_send=None
            self.chicard=None  
        else:
            p.handcard[j] = p.handcard[j] + 1
            p.pcg_list['chi'].append(jlist)
            self.broadcast(
                {"command": "other_chi", "pinfo": p.pinfo(), "indexcard": j}, passpid=[p.pid])
            self.cache_send=None
            self.chicard=None                  

    def _nextoutcard(self, pre):
        c = pre % self.maxplayer + 1
        for p in self.players.values():
            if c == p.onlyone:
                try:
                    i = self.cards.pop(random.randint(0, len(self.cards) - 1))
                    p.conn.sendMessage(json.dumps(
                        {"command": "getcard", "pinfo": p.pinfo(), "getcard": i}))                    
                    print 'nextcardend', p.handcard
                    # jieguo, _ = self.result_computer(p, i, p.onlyone)
                    # if 'angang' in jieguo or '+gang' in jieguo:
                    #     p.conn.sendMessage(json.dumps({"command": "selfgang", "c_action": jieguo, "indexcard": i}))
                    p.handcard[i] = p.handcard[i] + 1                            
                    if app.split.get_hu_info(p.handcard, 34, self.guicard):
                        print 'send zimohule'
                except IndexError as e:
                    print '########o', e
                except ValueError as e:
                    print 'no card get', e 
                    self.restart_game()    
                    self.broadcast({'command':'nocard'})              
                break

    def restart_game(self):
        self.banker=self.banker%self.maxplayer+1
        self.cache_send=None
        self.chicard=None 
        self.cards = None
        for p in self.players.values():
            p.handcard=[0 for i in xrange(34)]
            p.readystat=0
            self.pcg_list = {'chi': [], 'peng': [], 'gang': []}
           
                        


class player(object):
    # {readystat 0:没准备，1：准备}
    def __init__(self, pid, conn, readystat=0, onlyone=-1):
        self.pid = pid
        self.conn = conn
        self.readystat = readystat
        self.handcard = [0 for i in xrange(34)]
        self.onlyone = onlyone
        self.pcg_list = {'chi': [], 'peng': [], 'gang': []}

    def pinfo(self, items=None):
        info = {}
        if items == None:
            items = ["conn", "handcard"]
        for key in self.__dict__:
            if key in items:
                pass
            else:
                info[key] = self.__dict__[key]
        return info
