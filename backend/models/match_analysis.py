# backend/models/match_analysis.py
from sqlalchemy import Column, Integer, String, Date, Float, JSON
from sqlalchemy.sql import func
from utils.database import Base

class MatchAnalysis(Base):
    __tablename__ = 'match_analysis'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer)
    home_team_id = Column(Integer)
    away_team_id = Column(Integer)
    match_date = Column(Date)
    video_path = Column(String(255))
    
    # General match stats
    home_possession_percentage = Column(Float)
    away_possession_percentage = Column(Float)
    home_pass_accuracy = Column(Float)
    away_pass_accuracy = Column(Float)
    home_shots = Column(Integer)
    away_shots = Column(Integer)
    home_shots_on_target = Column(Integer)
    away_shots_on_target = Column(Integer)
    
    # Formation analysis
    home_formation = Column(String(10))
    away_formation = Column(String(10))
    home_formation_changes = Column(Integer)
    away_formation_changes = Column(Integer)
    
    # Player position heatmaps
    home_heatmap = Column(JSON)
    away_heatmap = Column(JSON)
    
    # Time-based stats
    possession_timeline = Column(JSON)
    formation_changes = Column(JSON)
    
    created_at = Column(Date, server_default=func.now())
    updated_at = Column(Date, onupdate=func.now())

    def __init__(self, match_id=None, home_team_id=None, away_team_id=None, match_date=None, 
                 video_path=None, home_possession_percentage=0, away_possession_percentage=0,
                 home_pass_accuracy=0, away_pass_accuracy=0, home_shots=0, away_shots=0,
                 home_shots_on_target=0, away_shots_on_target=0, home_formation=None,
                 away_formation=None, home_formation_changes=0, away_formation_changes=0,
                 home_heatmap=None, away_heatmap=None, possession_timeline=None,
                 formation_changes=None):
        self.match_id = match_id
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.match_date = match_date
        self.video_path = video_path
        self.home_possession_percentage = home_possession_percentage
        self.away_possession_percentage = away_possession_percentage
        self.home_pass_accuracy = home_pass_accuracy
        self.away_pass_accuracy = away_pass_accuracy
        self.home_shots = home_shots
        self.away_shots = away_shots
        self.home_shots_on_target = home_shots_on_target
        self.away_shots_on_target = away_shots_on_target
        self.home_formation = home_formation
        self.away_formation = away_formation
        self.home_formation_changes = home_formation_changes
        self.away_formation_changes = away_formation_changes
        self.home_heatmap = home_heatmap
        self.away_heatmap = away_heatmap
        self.possession_timeline = possession_timeline
        self.formation_changes = formation_changes