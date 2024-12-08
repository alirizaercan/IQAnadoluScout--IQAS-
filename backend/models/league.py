# backend/models/league.py
from sqlalchemy import Column, String, Integer
from utils.database import Base
from sqlalchemy.orm import relationship

class League(Base):
    __tablename__ = 'leagues'

    league_id = Column(String(10), primary_key=True)
    league_name = Column(String(100), nullable=False)
    league_logo_path = Column(String(250), nullable=True)
    country = Column(String(50), nullable=True)
    num_teams = Column(String(25), nullable=True)
    players = Column(Integer, nullable=True)
    foreign_players = Column(Integer, nullable=True)
    avg_marketing_val = Column(String(20), nullable=True)
    avg_age = Column(Integer, nullable=True)
    most_valuable_player = Column(String(50), nullable=True)
    total_market_value = Column(String(20), nullable=True)

    football_teams = relationship('FootballTeam', back_populates='league')
    footballers = relationship('Footballer', back_populates='league')

    def __init__(self, league_id, league_name, league_logo_path=None, country=None, num_teams=None, players=None, 
                 foreign_players=None, avg_marketing_val=None, avg_age=None, most_valuable_player=None, 
                 total_market_value=None):
        self.league_id = league_id
        self.league_name = league_name
        self.league_logo_path = league_logo_path
        self.country = country
        self.num_teams = num_teams
        self.players = players
        self.foreign_players = foreign_players
        self.avg_marketing_val = avg_marketing_val
        self.avg_age = avg_age
        self.most_valuable_player = most_valuable_player
        self.total_market_value = total_market_value
