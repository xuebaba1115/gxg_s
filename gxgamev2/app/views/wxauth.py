from app import db,app
from app.models.users_models import User
from flask import Flask,Blueprint, render_template,abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
import requests,json
from app.utiles import WXBizDataCrypt


auth = HTTPBasicAuth()


users = Blueprint('users', __name__,template_folder='templates')

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True   

@users.route('/')
def page_home():
    return render_template('index.html')

@users.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username })

@users.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@users.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

@users.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


@users.route('/api/wxauth')
def wxauth():
    try:
        qcode=request.headers['X-WX-Code']
        encryptedData=request.headers['X-WX-Encrypted-Data']
        iv=request.headers['X-WX-IV']
    except Exception as e:
        log.msg(str(e))
        abort(400)

    appId = app.config['WX_APPID']
    secret= app.config['WX_SECRET']
    getsession = u'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code'%(appId,secret,qcode)
    r=requests.get(getsession)
    res = json.loads(r.text) 
    sessionKey =res["session_key"]
    openid = res["openid"]
    
    pc = WXBizDataCrypt(appId, sessionKey)
    print pc.decrypt(encryptedData, iv)

    return "ssa"
