# backend/controllers/auth_controller.py
from flask import Blueprint, request, jsonify
from services.auth_service import login_user, register_user

auth_controller = Blueprint('auth_controller', __name__)

@auth_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = login_user(username, password)
    if user:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@auth_controller.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    role = data.get('role')
    club = data.get('club')

    # Register the user with all attributes
    user = register_user(
        username=username,
        email=email,
        password=password,
        firstname=firstname,
        lastname=lastname,
        role=role,
        club=club
    )

    if user:
        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'role': user.role,
                'club': user.club,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201
    return jsonify({'message': 'Error during registration'}), 400
