import base64
import json
from Crypto.Cipher import AES
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


class jm_jm(object):
    def __init__(self, ss):
        self.ssvi = ss

    @classmethod
    def hash_txt(self, txt):
        self.password_hash = pwd_context.encrypt(txt)

    @classmethod
    def verify_txt(self, txt):
        return pwd_context.verify(txt, self.password_hash)

    @classmethod
    def generate_auth_token(self, pwd,expiration=600):
        s = Serializer('gxgamgv2', expires_in=expiration)
        return s.dumps({'id': pwd})

    @classmethod
    def verify_auth_token(token):
        s = Serializer('gxgamev2')
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        return data