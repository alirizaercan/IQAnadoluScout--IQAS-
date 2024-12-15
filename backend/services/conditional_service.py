# backend/services/conditional_service.py
from models.league import League
from models.football_team import FootballTeam
from models.footballer import Footballer
from models.conditional import Conditional
from sqlalchemy.orm import Session

class ConditionalService:
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
        return [{"footballer_id": f.footballer_id, "footballer_name": f.footballer_name, "footballer_img_path": f.footballer_img_path, "nationality_img_path": f.nationality_img_path, "birthday": f.birthday} for f in footballers]

    def get_conditional_data(self, footballer_id, graph_type, start_date, end_date):
        query = self.session.query(Conditional).filter(
            Conditional.footballer_id == footballer_id,
            Conditional.created_at.between(start_date, end_date)
        )

        # Adjust data based on graph_type
        if graph_type == "VO2 Max Progression Over 30 Days":
            query = query.with_entities(Conditional.vo2_max, Conditional.lactate_levels, Conditional.created_at)
        elif graph_type == "Daily Lactate Levels Monitoring":
            query = query.with_entities(Conditional.vo2_max, Conditional.lactate_levels, Conditional.created_at)
        elif graph_type == "Training Intensity Progression":
            query = query.with_entities(Conditional.training_intensity, Conditional.created_at)
        elif graph_type == "Recovery Distribution":
            query = query.with_entities(Conditional.recovery_times, Conditional.created_at)
        elif graph_type == "VO2 Max Trend with Regression":
            query = query.with_entities(Conditional.vo2_max, Conditional.created_at)
        elif graph_type == "Conditional Goal Progress Overview":
            query = query.with_entities(Conditional.current_vo2_max, Conditional.current_lactate_levels, Conditional.current_muscle_strength, Conditional.target_vo2_max, Conditional.target_lactate_level, Conditional.target_muscle_strength, Conditional.created_at)

        return [row._asdict() for row in query]