import hashlib
from html import escape
from flask import Blueprint, Flask, current_app, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user

from server.db_operations import db_create_user, db_get_user_by_username
from server.auth.user import User

login_routes = Blueprint('auth', __name__)
CORS(login_routes, supports_credentials=True)

@login_routes.route('/auth/login', methods=['POST'])
def login():
    # Validate content type, prevent CSRF
    if not request.is_json:
        return jsonify({"error": "Invalid content type"}), 400
    
    data = request.get_json()
    
    username = data['username']
    password = data['password']

    user_data = db_get_user_by_username(username, current_app.user_collection)

    try:
        valid = User.check_password(user_data['password_hash'], password)
    except:
        valid = False

    if valid:
        user = User(_id=str(user_data['_id']), 
                    username=user_data['username'], 
                    password_hash=user_data['password_hash'],
                    lists=user_data.get('lists')
                    )
        login_user(user)
        return jsonify({"message": "User logged in", "user": user.data()}), 201
    return jsonify({"error": "Invalid credentials"}), 401

@login_routes.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "User logged out"}), 201

@login_routes.route('/auth/create_user', methods=['POST'])
def create_user():

    # Validate content type
    if not request.is_json:
        return jsonify({"error": "Invalid content type"}), 400

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    def sanitize_input(input_string):
        return escape(input_string.strip())

    username = sanitize_input(username)
    email = sanitize_input(email)
    password = sanitize_input(password)

    if not username or not email or not password:
        return jsonify({"error": "Missing one or more required fields"}), 400
    user = { 'username': username, 'password_hash': User.hash_password(password), 'email': email }
    # TODO: Check if username exists!
    result = db_create_user(user, current_app.user_collection)
    if result:
        return jsonify({"message": "User created"}), 201
    else: 
        return jsonify({"error": "Failed to create user"}), 401