# backend/services/auth_service.py
import os
import secrets
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from models.football_team import FootballTeam
from utils.database import Database

db_session = Database().connect()

def login_user(username_or_key, password):
    # First try to find user by username
    user = db_session.query(User).filter(User.username == username_or_key).first()
    
    # If not found by username, try by access_key (for club staff)
    if not user:
        user = db_session.query(User).filter(User.access_key == username_or_key).first()
        # If using access_key, we don't need password check
        if user:
            # Update login attempts and 'is_now_login'
            user.login_attempt += 1
            user.is_now_login = 'yes'
            db_session.commit()
            return user
    elif user and check_password_hash(user.password, password):
        # Update login attempts and 'is_now_login'
        user.login_attempt += 1
        user.is_now_login = 'yes'
        db_session.commit()
        return user
    return None

def create_admin_account(username, email, password, firstname=None, lastname=None):
    if db_session.query(User).filter((User.username == username) | (User.email == email)).first():
        return None  # Username or email already in use
    
    hashed_password = generate_password_hash(password)
    new_admin = User(
        username=username,
        email=email,
        password=hashed_password,
        firstname=firstname,
        lastname=lastname,
        role="admin",
        is_admin=True
    )
    db_session.add(new_admin)
    db_session.commit()
    return new_admin

def generate_access_key():
    # Generate a random 32-byte (64 hex characters) access key
    return secrets.token_hex(32)

def create_club_user(username, email, firstname, lastname, role, team_id):
    # Check if username or email already exists
    if db_session.query(User).filter((User.username == username) | (User.email == email)).first():
        return None, "Username or email already in use"
    
    # Check if team exists
    team = db_session.query(FootballTeam).filter(FootballTeam.team_id == team_id).first()
    if not team:
        return None, "Team not found"
    
    # Generate access key
    access_key = generate_access_key()
    
    # Access key'i password olarak kullan
    hashed_password = generate_password_hash(access_key)
    
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        firstname=firstname,
        lastname=lastname,
        role=role,
        club=team.team_name,
        team_id=team_id,
        access_key=access_key,
        is_admin=False,
        needs_password_change=True  # Kullanıcı ilk girişte şifresini değiştirmeli
    )
    
    db_session.add(new_user)
    db_session.commit()
    
    return new_user, access_key

def change_password(user_id, new_password):
    user = db_session.query(User).filter(User.id == user_id).first()
    if user:
        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        user.needs_password_change = False
        user.access_key = None  # Access key'i sil çünkü artık ihtiyaç yok
        db_session.commit()
        return True
    return False

def get_all_teams():
    return db_session.query(FootballTeam).all()

def get_all_users():
    return db_session.query(User).filter(User.is_admin == False).all()

def get_user_by_id(user_id):
    return db_session.query(User).filter(User.id == user_id).first()

def delete_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        db_session.delete(user)
        db_session.commit()
        return True
    return False

def get_user_settings(user_id):
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        return None
        
    settings = {
        'notifications': {
            'email': user.email,
            'wrong_login_attempt': user.wrong_login_attempt,
            'is_now_login': user.is_now_login
        },
        'account': {
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'role': user.role,
            'club': user.club,
        },
        'security': {
            'last_login': user.login_attempt,
            'two_factor_auth': False  # Gelecekte eklenebilir
        }
    }
    return settings

def update_user_settings(user_id, settings):
    try:
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"
        
        # Validate settings data structure
        if not isinstance(settings, dict):
            return False, "Invalid settings format"
        
        # Update account settings
        if 'account' in settings:
            account = settings['account']
            if 'firstname' in account and isinstance(account['firstname'], str):
                user.firstname = account['firstname']
            if 'lastname' in account and isinstance(account['lastname'], str):
                user.lastname = account['lastname']
        
        # Update notification settings
        if 'notifications' in settings:
            notifications = settings['notifications']
            if 'email' in notifications and isinstance(notifications['email'], str):
                user.email = notifications['email']
        
        # Save changes
        try:
            db_session.commit()
            return True, "Settings updated successfully"
        except Exception as e:
            db_session.rollback()
            print(f"Database error during settings update: {str(e)}")
            return False, "Database error occurred"
            
    except Exception as e:
        print(f"Settings update service error: {str(e)}")
        return False, str(e)

def create_notification(user_id, message):
    from models.notification import Notification
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    notification = Notification(user_id=user_id, message=message)
    db_session.add(notification)
    db_session.commit()
    return notification

def get_user_notifications(user_id):
    from models.notification import Notification
    return db_session.query(Notification)\
        .filter(Notification.user_id == user_id)\
        .order_by(Notification.created_at.desc())\
        .all()

def mark_notification_read(notification_id):
    from models.notification import Notification
    notification = db_session.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.read = True
        db_session.commit()
        return True
    return False

def create_broadcast_notification(message, exclude_admin=True):
    """Send a notification to all users (except admins by default)"""
    from models.notification import Notification
    users = db_session.query(User)
    if exclude_admin:
        users = users.filter(User.is_admin == False)
    users = users.all()
    
    notifications = []
    for user in users:
        notification = Notification(user_id=user.id, message=message)
        notifications.append(notification)
    
    db_session.bulk_save_objects(notifications)
    db_session.commit()
    return True