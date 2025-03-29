# backend/models/match.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from utils.database import Base

class Match(Base):
    __tablename__ = 'matches'
    
    match_id = Column(Integer, primary_key=True)
    league_id = Column(String(10), ForeignKey('leagues.league_id'), nullable=False)
    week = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    home_team_id = Column(Integer, ForeignKey('football_teams.team_id'), nullable=False)
    home_team = Column(String(50), nullable=False)
    home_goals = Column(Integer, nullable=True)
    away_team_id = Column(Integer, ForeignKey('football_teams.team_id'), nullable=False)
    away_team = Column(String(50), nullable=False)
    away_goals = Column(Integer, nullable=True)
    season = Column(String(10), nullable=False)
    home_footballer_id = Column(Integer, ForeignKey('footballers.footballer_id'), nullable=True)
    away_footballer_id = Column(Integer, ForeignKey('footballers.footballer_id'), nullable=True)
    is_played = Column(Boolean, default=False)

    # Relationships
    league = relationship('League', back_populates='matches')
    home_team_rel = relationship('FootballTeam', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team_rel = relationship('FootballTeam', foreign_keys=[away_team_id], back_populates='away_matches')
    home_footballer = relationship('Footballer', foreign_keys=[home_footballer_id], back_populates='home_matches')
    away_footballer = relationship('Footballer', foreign_keys=[away_footballer_id], back_populates='away_matches')

    def __init__(self, league_id, week, date, home_team_id, home_team, home_goals, 
                 away_team_id, away_team, away_goals, season, 
                 home_footballer_id=None, away_footballer_id=None, is_played=False):
        self.league_id = league_id
        self.week = week
        self.date = date
        self.home_team_id = home_team_id
        self.home_team = home_team
        self.home_goals = home_goals
        self.away_team_id = away_team_id
        self.away_team = away_team
        self.away_goals = away_goals
        self.season = season
        self.home_footballer_id = home_footballer_id
        self.away_footballer_id = away_footballer_id
        self.is_played = is_played