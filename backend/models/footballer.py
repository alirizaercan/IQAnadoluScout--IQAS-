# backend/models/footballer.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base

class Footballer(Base):
    __tablename__ = 'footballers'

    footballer_id = Column(Integer, primary_key=True)
    league_id = Column(String, ForeignKey('leagues.league_id'), nullable=False)
    team_id = Column(Integer, ForeignKey('football_teams.team_id'), nullable=False)
    footballer_name = Column(String, nullable=False)
    club = Column(String, nullable=False)
    league_name = Column(String, nullable=True)
    trikot_num = Column(String(5), nullable=True)
    position = Column(String(50), nullable=True)
    birthday = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    nationality_img_path = Column(String(250), nullable=True)
    height = Column(String(10), nullable=True)
    feet = Column(String(10), nullable=True)
    contract = Column(String(50), nullable=True)
    market_value = Column(String(20), nullable=True)
    footballer_img_path = Column(String(250), nullable=True)

    league = relationship('League', back_populates='footballers')
    team = relationship('FootballTeam', back_populates='footballers')

    def __init__(self, league_id, team_id, footballer_name, club, league_name=None, trikot_num=None, position=None, 
                 birthday=None, age=None, nationality_img_path=None, height=None, feet=None, contract=None, 
                 market_value=None, footballer_img_path=None):
        self.league_id = league_id
        self.team_id = team_id
        self.footballer_name = footballer_name
        self.club = club
        self.league_name = league_name
        self.trikot_num = trikot_num
        self.position = position
        self.birthday = birthday
        self.age = age
        self.nationality_img_path = nationality_img_path
        self.height = height
        self.feet = feet
        self.contract = contract
        self.market_value = market_value
        self.footballer_img_path = footballer_img_path
