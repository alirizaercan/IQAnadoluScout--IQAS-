# backend/models/match_analysis.py
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, TIMESTAMP, text
from sqlalchemy.orm import relationship
from utils.database import Base

class MatchAnalysis(Base):
    __tablename__ = 'match_analysis'
    
    id = Column(Integer, primary_key=True)
    match_date = Column(Date, nullable=False)
    home_team_id = Column(Integer, ForeignKey('football_teams.team_id'))
    home_team_name = Column(String(100), nullable=False)
    away_team_id = Column(Integer, ForeignKey('football_teams.team_id'))
    away_team_name = Column(String(100), nullable=False)
    video_path = Column(String(255), nullable=False)
    processed_video_path = Column(String(255))
    
    # Team possession statistics
    home_possession_percentage = Column(Float)
    away_possession_percentage = Column(Float)
    home_attack_phases = Column(Integer)
    away_attack_phases = Column(Integer)
    
    # Formation analysis
    home_formation = Column(String(20))
    away_formation = Column(String(20))
    home_avg_player_positions = Column(JSON)
    away_avg_player_positions = Column(JSON)
    
    # Ball control statistics
    home_ball_control_time = Column(Float)
    away_ball_control_time = Column(Float)
    
    # Player speed/distance
    home_avg_speed = Column(Float)
    away_avg_speed = Column(Float)
    home_total_distance = Column(Float)
    away_total_distance = Column(Float)
    
    # Team colors
    home_team_color = Column(String(20))
    away_team_color = Column(String(20))
    
    # Tactical heatmaps
    home_heatmap = Column(JSON)
    away_heatmap = Column(JSON)
    
    # Key moments analysis
    key_moments = Column(JSON)
    
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationships
    home_team = relationship('FootballTeam', foreign_keys=[home_team_id])
    away_team = relationship('FootballTeam', foreign_keys=[away_team_id])
    
    def __init__(self, **kwargs):
        # Required fields
        self.match_date = kwargs.get('match_date')
        self.home_team_id = kwargs.get('home_team_id')
        self.home_team_name = kwargs.get('home_team_name')
        self.away_team_id = kwargs.get('away_team_id')
        self.away_team_name = kwargs.get('away_team_name')
        self.video_path = kwargs.get('video_path')
        
        # Optional fields
        self.processed_video_path = kwargs.get('processed_video_path')
        
        # Statistics fields
        self.home_possession_percentage = kwargs.get('home_possession_percentage')
        self.away_possession_percentage = kwargs.get('away_possession_percentage')
        self.home_attack_phases = kwargs.get('home_attack_phases')
        self.away_attack_phases = kwargs.get('away_attack_phases')
        self.home_formation = kwargs.get('home_formation')
        self.away_formation = kwargs.get('away_formation')
        self.home_avg_player_positions = kwargs.get('home_avg_player_positions')
        self.away_avg_player_positions = kwargs.get('away_avg_player_positions')
        self.home_ball_control_time = kwargs.get('home_ball_control_time')
        self.away_ball_control_time = kwargs.get('away_ball_control_time')
        self.home_avg_speed = kwargs.get('home_avg_speed')
        self.away_avg_speed = kwargs.get('away_avg_speed')
        self.home_total_distance = kwargs.get('home_total_distance')
        self.away_total_distance = kwargs.get('away_total_distance')
        self.home_team_color = kwargs.get('home_team_color')
        self.away_team_color = kwargs.get('away_team_color')
        self.home_heatmap = kwargs.get('home_heatmap')
        self.away_heatmap = kwargs.get('away_heatmap')
        self.key_moments = kwargs.get('key_moments')