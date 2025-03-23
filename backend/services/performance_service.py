# backend/services/performance_service.py
from models.league import League
from models.football_team import FootballTeam
from models.footballer import Footballer
from models.performance import Performance
from sqlalchemy.orm import Session
import pandas as pd

class PerformanceService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_all_leagues(self):
        leagues = self.session.query(League).all()
        return [{"league_id": league.league_id, "league_name": league.league_name, "league_logo_path": league.league_logo_path} for league in leagues]
    
    def get_teams_by_league(self, league_id):
        teams = self.session.query(FootballTeam).filter_by(league_id=league_id).all()
        return [{"team_id": team.team_id, "team_name": team.team_name, "img_path": team.img_path} for team in teams]
    
    def get_footballers_by_team(self, team_id):
        footballers = self.session.query(Footballer).filter_by(team_id=team_id).all()
        return [{"footballer_id": f.footballer_id, "footballer_name": f.footballer_name, "footballer_img_path": f.footballer_img_path, "nationality_img_path": f.nationality_img_path, "birthday": f.birthday.strftime('%d %B %Y')} for f in footballers]
    
    def get_footballer_performance_data(self, footballer_id, graph_type):
        """Get performance data for a footballer and specific graph type."""
        # Query the entire performance record for the footballer
        performance = self.session.query(Performance).filter(
            Performance.footballer_id == footballer_id
        ).first()
        
        if not performance:
            return []
        
        # Convert to dictionary
        performance_dict = self._performance_to_dict(performance)
        
        # Select only the relevant fields based on graph_type
        if graph_type == "Goals and Assists Analysis":
            return [{'goals': performance_dict.get('goals', 0),
                    'assists': performance_dict.get('assists', 0)}]
                    
        elif graph_type == "Shooting Accuracy Analysis":
            return [{'shots_per_game': performance_dict.get('shots_per_game', 0),
                    'shots_on_target_per_game': performance_dict.get('shots_on_target_per_game', 0)}]
                    
        elif graph_type == "Defensive Performance Analysis":
            return [{'tackles_per_game': performance_dict.get('tackles_per_game', 0),
                    'interceptions_per_game': performance_dict.get('interceptions_per_game', 0),
                    'clearances_per_game': performance_dict.get('clearances_per_game', 0)}]
                    
        elif graph_type == "Passing Accuracy Analysis":
            return [{'accurate_per_game': performance_dict.get('accurate_per_game', 0),
                    'acc_long_balls': performance_dict.get('acc_long_balls', 0),
                    'acc_crosses': performance_dict.get('acc_crosses', 0)}]
                    
        elif graph_type == "Dribbling Success Analysis":
            return [{
                'succ_dribbles': performance_dict.get('succ_dribbles', 0),
                'dribbled_past_per_game': performance_dict.get('dribbled_past_per_game', 0),
                'total_played': performance_dict.get('total_played', 0),
                'possession_lost': performance_dict.get('possession_lost', 0),
                'possession_won_final_third': performance_dict.get('possession_won_final_third', 0)
            }]
                    
        elif graph_type == "Playing Time Analysis":
            return [{
                'total_played': performance_dict.get('total_played', 0),
                'started': performance_dict.get('started', 0),
                'minutes_per_game': performance_dict.get('minutes_per_game', 0),
                'total_minutes_played': performance_dict.get('total_minutes_played', 0)
            }]
        
        elif graph_type == "Physical Duels Analysis":
            return [{'total_duels_won': performance_dict.get('total_duels_won', 0),
                    'ground_duels_won': performance_dict.get('ground_duels_won', 0),
                    'aerial_duels_won': performance_dict.get('aerial_duels_won', 0)}]
                    
        elif graph_type == "Error Analysis":
            return [{'errors_leading_to_shot': performance_dict.get('errors_leading_to_shot', 0),
                    'errors_leading_to_goal': performance_dict.get('errors_leading_to_goal', 0)}]
                    
        elif graph_type == "Disciplinary Analysis":
            return [{
                'yellow': performance_dict.get('yellow', 0),
                'yellow_red': performance_dict.get('yellow_red', 0),  # Added yellow-red cards
                'red_cards': performance_dict.get('red_cards', 0),
                'fouls': performance_dict.get('fouls', 0),            # Added fouls
                'was_fouled': performance_dict.get('was_fouled', 0),  # Added was fouled
                'total_played': performance_dict.get('total_played', 0)  # For calculating ratios
            }]
                    
        elif graph_type == "Overall Performance Radar Analysis":
            return [{'goals_per_game': performance_dict.get('goals_per_game', 0),
                    'assists': performance_dict.get('assists', 0),
                    'tackles_per_game': performance_dict.get('tackles_per_game', 0),
                    'interceptions_per_game': performance_dict.get('interceptions_per_game', 0),
                    'accurate_per_game': performance_dict.get('accurate_per_game', 0)}]
                    
        # Return all data if graph type is not recognized
        return [performance_dict]
    
    def _performance_to_dict(self, performance):
        """Convert a Performance object to a dictionary."""
        if not performance:
            return {}
            
        return {c.name: getattr(performance, c.name) for c in performance.__table__.columns}