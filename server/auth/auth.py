from flask import Blueprint, Flask, current_app, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from .user import User

login_routes = Blueprint('/auth', __name__)
# login_manager = current_app.login_manager

@login_routes.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.get_user_by_name(username, current_app.user_collection)
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('dashboard'))  # Example route after login
    return 'Invalid credentials', 401

@login_routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))  # Redirect after logout
