# backend/models/__init__.py
from sqlalchemy.ext.declarative import declarative_base

# Create a single declarative base for all models
Base = declarative_base()

# Import all models in dependency order to register them
# This ensures foreign key relationships are handled correctly

# First: Base tables without foreign keys
from .user import User
from .league import League
from .football_team import FootballTeam

# Second: Tables with foreign keys to base tables  
from .footballer import Footballer
from .notification import Notification

# Third: Tables with foreign keys to footballer/team
from .player import Player
from .match import Match
from .performance import Performance
from .physical import Physical
from .endurance import Endurance
from .conditional import Conditional
from .match_analysis import MatchAnalysis

# Export all models
__all__ = [
    'Base',
    'User',
    'League', 
    'FootballTeam',
    'Footballer',
    'Notification',
    'Player',
    'Match',
    'Performance',
    'Physical',
    'Endurance',
    'Conditional',
    'Scouting',
    'Transfer',
    'MatchAnalysis'
]
