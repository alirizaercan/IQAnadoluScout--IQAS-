# backend/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    old_password = Column(String(255))
    wrong_login_attempt = Column(Integer, default=0)
    login_attempt = Column(Integer, default=0)
    is_now_login = Column(String(20), default='no')
    role = Column(String(25))
    club = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, username, email, password, firstname=None, lastname=None, role=None, club=None):
        self.username = username
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.role = role
        self.club = club