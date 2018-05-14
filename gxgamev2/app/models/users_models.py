# coding:utf8
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer('gxgamgv2', expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer('gxgamev2')
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


class WXUser(db.Model):
    __tablename__ = 'wxusers'
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(32), index=True)
    province = db.Column(db.String(32))
    city = db.Column(db.String(32))
    avatarUrl = db.Column(db.String(64))
    country = db.Column(db.String(32))
    nickName = db.Column(db.String(32))
    gender = db.Column(db.Integer)
    gamestatus = db.Column(db.Integer,default=0) #0:noplay #1:play
    userstatus = db.Column(db.Integer,default=0) #0:weixin #1:youke
    roomid = db.Column(db.Integer)
