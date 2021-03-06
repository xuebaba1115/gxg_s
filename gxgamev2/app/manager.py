# coding:utf8
from twisted.python import log
from autobahn.twisted.websocket import protocol
import json


class ConnectionManager:
    """ 连接管理器
    @param _connections: dict {connID:conn Object}管理的所有连接
    """

    def __init__(self):
        """初始化
        @param _connections: dict {connID:conn Object}
        """
        self._connections = {}

    def getNowConnCnt(self):
        """获取当前连接数量"""
        return len(self._connections.items())

    def addConnection(self, conn):
        """加入一条连接
        @param _conn: Conn object
        """
        _conn = Connection(conn)
        if _conn.id in self._connections:
            raise Exception("系统记录冲突")
        self._connections[_conn.id] = _conn
        return _conn.id

    def dropConnectionByID(self, connID):
        """根据连接的id删除连接实例
        @param connID: int 连接的id
        """
        try:
            self.loseConnection(connID)
            del self._connections[connID]
        except Exception as e:
            log.msg(str(e))

    def getConnectionByID(self, connID):
        """根据ID获取一条连接
        @param connID: int 连接的id
        """
        return self._connections.get(connID, None)

    def loseConnection(self, connID):
        """根据连接ID主动端口与客户端的连接
        """
        conn = self.getConnectionByID(connID)
        if conn:
            conn.loseConnection()

    def pushObjectall(self, msg):
        """主动推送all消息
        """
        for target in self._connections:
            try:
                conn = self.getConnectionByID(target)
                if conn:
                    conn.preparedData(msg)
            except Exception, e:
                log.err(str(e))

    def pushObjectbyconnIDlist(self, msg, sendlist):
        """主动推送消息list
        """
        for target in sendlist:
            try:
                conn = self.getConnectionByID(target)
                if conn:
                    conn.preparedData(msg)
            except Exception, e:
                log.err(str(e))

    def pushObjectbyconnID(self, msg,idlist):
        """主动推送消息connid
        """
        for target in idlist:
            try:
                conn = self.getConnectionByID(target)
                if conn:
                    conn.safeData(msg)
            except Exception, e:
                log.err(str(e))


class Connection:
    """
    """
    def __init__(self, _conn):
        """
        id 连接的ID
        transport 连接的通道
        """
        self.id = _conn.transport.sessionno
        self.instance = _conn

    def loseConnection(self):
        """断开与客户端的连接
        """
        self.instance.transport.loseConnection()

    def safeData(self, msg):
        """发送消息
        """
        self.instance.sendMessage(json.dumps(msg).encode('utf8'))

    def preparedData(self, msg):
        """发送消息
        """
        self.instance.sendPreparedMessage(msg)
        # print("prepared message sent to {}".format(self.instance.peer))
