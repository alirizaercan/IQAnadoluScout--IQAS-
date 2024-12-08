# backend/services/physical_service.py
from models.league import League
from models.football_team import FootballTeam
from models.footballer import Footballer
from models.physical import Physical
from sqlalchemy.orm import Session

class PhysicalService:
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

    def get_physical_data(self, footballer_id, graph_type, start_date, end_date):
        query = self.session.query(Physical).filter(
            Physical.footballer_id == footballer_id,
            Physical.created_at.between(start_date, end_date)
        )

        # Adjust data based on graph_type
        if graph_type == "Physical Progress Tracker":
            query = query.with_entities(Physical.muscle_mass, Physical.muscle_strength, Physical.muscle_endurance, Physical.flexibility, Physical.created_at)
        elif graph_type == "Body Composition Progress Tracker":
            query = query.with_entities(Physical.weight, Physical.height, Physical.muscle_mass, Physical.created_at)
        # Add other graph types here...

        return [row._asdict() for row in query]
