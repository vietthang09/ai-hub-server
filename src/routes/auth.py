from flask import Blueprint
from src.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)
auth_controller = AuthController()

@auth_bp.route('/register', methods=['POST'])
def register():
    return auth_controller.register()

@auth_bp.route('/login', methods=['POST'])
def login():
    return auth_controller.login()

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    return auth_controller.refresh_token()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return auth_controller.logout()