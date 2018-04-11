import uuid
import sys,os

from run import app,cache
from models import User,db,auth

from flask import Flask, render_template,abort, request, jsonify, g, url_for
from flask_cache import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth






@app.route('/')
@cache.cached(timeout=60)
def page_home():
    return render_template('index.html')

@app.route('/api/users', methods = ['POST'])
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

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })