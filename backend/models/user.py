# backend/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models import Base
from models.notification import Notification  # Add this import

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    firstname = Column(String(50))
    lastname = Column(String(50))
    email = Column(String(50), unique=True, nullable=False)
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    password = Column(String(255), nullable=False)
    old_password = Column(String(255))
    wrong_login_attempt = Column(Integer, default=0)
    login_attempt = Column(Integer, default=0)
    is_now_login = Column(String(20), default='no')
    role = Column(String(25))
    club = Column(String(100))
    team_id = Column(Integer, ForeignKey('football_teams.team_id'))
    access_key = Column(String(64), unique=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    needs_password_change = Column(Boolean, default=False)
    
    # The relationship with FootballTeam is defined in FootballTeam with backref
    # We do not need to explicitly define it here

    def __init__(self, username, email, password, firstname=None, lastname=None, 
                 role=None, club=None, team_id=None, access_key=None, is_admin=False,
                 needs_password_change=False):
        self.username = username
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.role = role
        self.club = club
        self.team_id = team_id
        self.access_key = access_key
        self.is_admin = is_admin
        self.needs_password_change = needs_password_change