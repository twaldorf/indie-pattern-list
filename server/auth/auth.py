import hashlib
from flask import Blueprint, Flask, current_app, jsonify, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user

from ..db_operations import db_create_user, db_get_user_by_username
from .user import User

login_routes = Blueprint('auth', __name__)
# login_manager = current_app.login_manager

@login_routes.route('/login', methods=['POST'])
def login():
    username = request.body['username']
    password = request.body['password']

    print(username)
    print(password)

    user_data = db_get_user_by_username(username)

    if User.check_password(user_data['password_hash'], password):
        user = User(_id=user_data._id, 
                    username=user_data.username, 
                    password_hash=user_data.password_hash, 
                    content=user_data.content)

    if user:
        login_user(user)
        next = request.args.get('next')
        return redirect('/index')
    return 'Invalid credentials', 401

@login_routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@login_routes.route('/auth/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = { 'username': username, 'password_hash': User.hash_password(password) }
    # TODO: Check if username exists
    result = db_create_user(user, current_app.user_collection)
    if result:
        return jsonify({"message": "User created"}), 201
    else: 
        return 'Failed to create user', 401