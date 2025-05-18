from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_cors import cross_origin
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import os
import datetime
from dotenv import load_dotenv
from services.auth_service import (
    login_user, 
    create_admin_account, 
    create_club_user,
    get_all_teams,
    get_all_users,
    get_user_by_id,
    delete_user,
    change_password,
    get_user_settings,
    update_user_settings,
    create_notification,  
    get_user_notifications,
    mark_notification_read,
    create_broadcast_notification
)

load_dotenv()
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

auth_controller = Blueprint('auth_controller', __name__)

# Decorator for routes that require admin access
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            print(f"Auth header: {auth_header}")
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            print("No token found in request")
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Oluşturulan serializer
            s = URLSafeTimedSerializer(JWT_SECRET_KEY)
            # Token'ı çözümle
            data = s.loads(token, max_age=86400)  # 24 saat = 86400 saniye
            print(f"Token data: {data}")
            
            if not data.get('is_admin'):
                print("User is not admin")
                return jsonify({'message': 'Admin privileges required'}), 403
            
            print("Admin access granted")
        except SignatureExpired:
            print("Token expired")
            return jsonify({'message': 'Token has expired'}), 401
        except BadSignature:
            print("Bad signature")
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            print(f"Token validation error: {str(e)}")
            return jsonify({'message': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    
    return decorated

@auth_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_key = data.get('username')
    password = data.get('password')
    
    if not username_or_key:
        return jsonify({'message': 'Username/Access key is required'}), 400
    
    user = login_user(username_or_key, password)
    
    if user:
        # Serialize user info with team data
        team_data = None
        if user.team:
            team_data = {
                'id': user.team.team_id,
                'name': user.team.team_name,
                'logo': user.team.img_path,
                'league': user.team.league_name
            }
          # Create token with explicit admin flag
        s = URLSafeTimedSerializer(JWT_SECRET_KEY)
        is_admin = bool(user.is_admin)  # Ensure it's a boolean
        print(f"Creating token for user_id={user.id}, is_admin={is_admin}")
        
        token = s.dumps({
            'user_id': user.id,
            'is_admin': is_admin
        })
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email,
                'role': user.role,
                'team': team_data,
                'is_admin': user.is_admin,
                'needs_password_change': user.needs_password_change
            }
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_controller.route('/change-password', methods=['POST', 'OPTIONS'])
def change_user_password():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    data = request.get_json()
    user_id = data.get('user_id')
    new_password = data.get('new_password')
    
    if not user_id or not new_password:
        return jsonify({'message': 'Missing required fields'}), 400
    
    if change_password(user_id, new_password):
        user = get_user_by_id(user_id)
        if user:
            response = jsonify({
                'message': 'Password changed successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'role': user.role,
                    'club': user.club,
                    'is_admin': user.is_admin,
                    'needs_password_change': user.needs_password_change
                }
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
    
    return jsonify({'message': 'Failed to change password'}), 400

@auth_controller.route('/admin/create', methods=['POST'])
def create_admin():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')    
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    
    # Only allow the first admin to be created without authentication
    existing_admins = get_all_users()
    admin_exists = any(user.is_admin for user in existing_admins)
    
    if admin_exists:
        # Check if request is from existing admin
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Admin authentication required'}), 401
        
        try:
            token = token.split(' ')[1]
            s = URLSafeTimedSerializer(JWT_SECRET_KEY)
            data = s.loads(token, max_age=86400)
            if not data.get('is_admin'):
                return jsonify({'message': 'Admin privileges required'}), 403
        except SignatureExpired:
            return jsonify({'message': 'Token has expired'}), 401
        except BadSignature:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception:
            return jsonify({'message': 'Invalid token'}), 401

    admin = create_admin_account(username, email, password, firstname, lastname)
    if admin:
        return jsonify({
            'message': 'Admin account created successfully',
            'admin': {
                'id': admin.id,
                'username': admin.username,
                'email': admin.email
            }
        }), 201
    
    return jsonify({'message': 'Error creating admin account, username or email may already exist'}), 400

@auth_controller.route('/admin/create-user', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    role = data.get('role')
    team_id = data.get('team_id')
    
    user, access_key = create_club_user(username, email, firstname, lastname, role, team_id)
    
    if user:
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'club': user.club,
                'team_id': user.team_id
            },
            'access_key': access_key
        }), 201
    
    return jsonify({'message': 'Error creating user'}), 400

@auth_controller.route('/admin/teams', methods=['GET'])
@admin_required
def teams():
    teams_list = get_all_teams()
    teams_data = [{
        'team_id': team.team_id,
        'team_name': team.team_name,
        'league_name': team.league_name
    } for team in teams_list]
    
    return jsonify({'teams': teams_data}), 200

@auth_controller.route('/admin/users', methods=['GET'])
@admin_required
def users():
    users_list = get_all_users()
    users_data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'role': user.role,
        'club': user.club,
        'team_id': user.team_id,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
    } for user in users_list]
    
    return jsonify({'users': users_data}), 200

@auth_controller.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def remove_user(user_id):
    if delete_user(user_id):
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@auth_controller.route('/static/team-logos/<path:filename>')
def serve_team_logo(filename):
    return send_from_directory('static/team-logos', filename)

@auth_controller.route('/settings', methods=['GET'])
def get_settings():
    token = request.headers.get('Authorization', '').split(" ")[1]
    if not token:
        return jsonify({'message': 'Token is required'}), 401
    
    try:
        s = URLSafeTimedSerializer(JWT_SECRET_KEY)
        data = s.loads(token, max_age=86400)
        user_id = data.get('user_id')
        
        settings = get_user_settings(user_id)
        if settings:
            return jsonify(settings), 200
        return jsonify({'message': 'Settings not found'}), 404
        
    except Exception as e:
        return jsonify({'message': str(e)}), 401

@auth_controller.route('/settings', methods=['PUT'])
def update_settings():
    try:
        # Get and validate token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Invalid token format'}), 401
            
        token = auth_header.split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is required'}), 401
        
        # Decode token and get user ID
        s = URLSafeTimedSerializer(JWT_SECRET_KEY)
        try:
            data = s.loads(token, max_age=86400)
            user_id = data.get('user_id')
        except:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        # Get and validate settings data
        settings_data = request.get_json()
        if not settings_data:
            return jsonify({'message': 'No settings data provided'}), 400
            
        required_fields = ['account', 'notifications']
        if not all(field in settings_data for field in required_fields):
            return jsonify({'message': 'Missing required settings fields'}), 400
            
        # Update settings
        success, message = update_user_settings(user_id, settings_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
            
        return jsonify({
            'success': False,
            'message': message
        }), 400
        
    except Exception as e:
        print(f"Settings update error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to update settings: {str(e)}'
        }), 500

@auth_controller.route('/notifications', methods=['GET'])
def get_notifications():
    token = request.headers.get('Authorization', '').split(" ")[1]
    if not token:
        return jsonify({'message': 'Token is required'}), 401
    
    try:
        s = URLSafeTimedSerializer(JWT_SECRET_KEY)
        data = s.loads(token, max_age=86400)
        user_id = data.get('user_id')
        
        notifications = get_user_notifications(user_id)
        result = [{
            'id': n.id,
            'message': n.message,
            'read': n.read,
            'created_at': n.created_at.isoformat()
        } for n in notifications]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 401

@auth_controller.route('/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_read(notification_id):
    token = request.headers.get('Authorization', '').split(" ")[1]
    if not token:
        return jsonify({'message': 'Token is required'}), 401
    
    try:
        s = URLSafeTimedSerializer(JWT_SECRET_KEY)
        s.loads(token, max_age=86400)  # Just verify token
        
        success = mark_notification_read(notification_id)
        if success:
            return jsonify({'message': 'Notification marked as read'}), 200
        return jsonify({'message': 'Notification not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 401

@auth_controller.route('/admin/notifications/broadcast', methods=['POST', 'OPTIONS'])
def broadcast_notification():
    # Allow OPTIONS requests for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    # POST request handling with added logging
    print(f"Headers received: {request.headers}")
    
    # Check for authorization before applying decorator
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        print(f"Auth header: {auth_header}")
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
    
    if not token:
        print("No token found in broadcast request")
        return jsonify({'message': 'Token is missing'}), 401
    
    # Verify admin privileges
    try:
        s = URLSafeTimedSerializer(JWT_SECRET_KEY)
        data = s.loads(token, max_age=86400)
        print(f"Token data in broadcast: {data}")
        
        if not data.get('is_admin'):
            print("User is not admin in broadcast")
            return jsonify({'message': 'Admin privileges required'}), 403
    except Exception as e:
        print(f"Token error in broadcast: {str(e)}")
        return jsonify({'message': 'Invalid token'}), 401
    
    # Process the notification after admin verification passed
    request_data = request.get_json()
    print(f"Request data: {request_data}")
    message = request_data.get('message')
    
    if not message:
        return jsonify({'message': 'Message is required'}), 400
    
    try:
        success = create_broadcast_notification(message)
        if success:
            print("Broadcast notification sent successfully")
            return jsonify({'message': 'Notification broadcast sent'}), 200
        print("Failed to send broadcast notification")
        return jsonify({'message': 'Failed to send broadcast'}), 500
    except Exception as e:
        print(f"Error creating broadcast: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500

# Additional debug endpoint for testing admin authentication
@auth_controller.route('/admin/test-auth', methods=['GET'])
def test_admin_auth():
    """Debug endpoint to test admin authentication"""
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
    
    if not token:
        return jsonify({
            'authenticated': False,
            'message': 'No token found'
        }), 401
    
    try:
        s = URLSafeTimedSerializer(JWT_SECRET_KEY)
        data = s.loads(token, max_age=86400)
        
        is_admin = data.get('is_admin', False)
        user_id = data.get('user_id')
        
        return jsonify({
            'authenticated': True,
            'is_admin': is_admin,
            'user_id': user_id,
            'message': 'Token is valid'
        })
        
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'message': f'Token error: {str(e)}'
        }), 401