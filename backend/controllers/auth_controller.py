# backend/controllers/auth_controller.py
from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
        self.auth_controller = Blueprint('auth_controller', __name__)

        self.auth_controller.add_url_rule('/register', 'register', self.register, methods=['POST'])
        self.auth_controller.add_url_rule('/login', 'login', self.login, methods=['POST'])
        self.auth_controller.add_url_rule('/logout', 'logout', self.logout, methods=['POST'])

    def register(self):
        data = request.get_json()
        response = self.auth_service.register(data)
        return jsonify(response), response['status']

    def login(self):
        data = request.get_json()
        response = self.auth_service.login(data)
        return jsonify(response), response['status']

    def logout(self):
        user_id = request.json.get('user_id')
        response = self.auth_service.logout(user_id)
        return jsonify(response), response['status']
