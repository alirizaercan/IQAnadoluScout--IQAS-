# backend/models/football_team.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class FootballTeam(Base):
    __tablename__ = 'football_teams'

    team_id = Column(Integer, primary_key=True)
    league_name = Column(String(100), nullable=False)  # league_name için 100 karakter
    league_id = Column(String(10), ForeignKey('leagues.league_id'), nullable=False)  # league_id için 10 karakter
    team_name = Column(String(100), nullable=False)  # team_name için 100 karakter
    team_info_link = Column(String(250), nullable=True)  # team_info_link için 250 karakter
    img_path = Column(String(250), nullable=True)  # img_path için 250 karakter
    num_players = Column(Integer, nullable=True)
    avg_age = Column(Integer, nullable=True)
    num_legionnaires = Column(Integer, nullable=True)
    avg_marketing_val = Column(String(20), nullable=True)  # avg_marketing_val için 20 karakter
    total_squad_value = Column(String(20), nullable=True)  # total_squad_value için 20 karakter

    league = relationship('League', back_populates='football_teams')
    footballers = relationship('Footballer', back_populates='team')
    home_matches = relationship('Match', foreign_keys='Match.home_team_id', back_populates='home_team')
    away_matches = relationship('Match', foreign_keys='Match.away_team_id', back_populates='away_team')

    def __init__(self, league_name, league_id, team_name, team_info_link=None, img_path=None, 
                 num_players=None, avg_age=None, num_legionnaires=None, avg_marketing_val=None, 
                 total_squad_value=None):
        self.league_name = league_name
        self.league_id = league_id
        self.team_name = team_name
        self.team_info_link = team_info_link
        self.img_path = img_path
        self.num_players = num_players
        self.avg_age = avg_age
        self.num_legionnaires = num_legionnaires
        self.avg_marketing_val = avg_marketing_val
        self.total_squad_value = total_squad_value
