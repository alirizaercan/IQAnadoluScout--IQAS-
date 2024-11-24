# backend/services/auth_service.py
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from utils.database import Database

db_session = Database().connect()

def login_user(username, password):
    user = db_session.query(User).filter(User.username == username).first()
    if user and check_password_hash(user.password, password):
        # Update login attempts and 'is_now_login'
        user.login_attempt += 1
        user.is_now_login = 'yes'
        db_session.commit()
        return user
    return None

def register_user(username, email, password, firstname=None, lastname=None, role=None, club=None):
    if db_session.query(User).filter((User.username == username) | (User.email == email)).first():
        return None  # Kullanıcı adı veya e-posta zaten kullanılmış
    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        firstname=firstname,
        lastname=lastname,
        role=role,
        club=club
    )
    db_session.add(new_user)
    db_session.commit()
    return new_user