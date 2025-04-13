# backend/controllers/score_prediction_controller.py
from flask import Blueprint, request, jsonify
from services.match_service import MatchService
from utils.database import Database
from models.football_team import FootballTeam
from models.league import League
from models.match import Match
from datetime import datetime, timedelta
import traceback

match_bp = Blueprint('match_score_prediction', __name__)
db = Database()

@match_bp.route('/leagues', methods=['GET'])
def get_leagues():
    session = db.connect()
    try:
        service = MatchService(session)
        leagues = service.get_all_leagues()
        return jsonify(leagues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@match_bp.route('/teams/<league_id>', methods=['GET'])
def get_teams(league_id):
    session = db.connect()
    try:
        service = MatchService(session)
        teams = service.get_teams_by_league(league_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@match_bp.route('/predictions/<team_id>', methods=['GET'])
def get_predictions(team_id):
    session = db.connect()
    try:
        team = session.query(FootballTeam).filter_by(team_id=team_id).first()
        if not team:
            return jsonify({'error': f'Team with ID {team_id} not found'}), 404
        
        # Get current date
        today = datetime.now().date()
        
        service = MatchService(session)
        
        # Find upcoming matches for next 4 weeks
        upcoming_matches = get_next_four_weeks_matches(session, team_id, today)
        
        # If no upcoming matches, get the last 4 played matches
        if not upcoming_matches:
            upcoming_matches = get_last_four_weeks_matches(session, team_id, today)
        
        # If we have matches, get predictions for them
        if upcoming_matches:
            # Use the existing prediction service but extract only the matches we want
            all_predictions = service.predict_match_scores(team_id)
            
            # Filter predictions to only include our target matches
            match_ids = [match.match_id for match in upcoming_matches]
            predictions = [pred for pred in all_predictions if pred['match_id'] in match_ids]
            
            # Sort by date
            predictions.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
            
            # Take only the first 4 if we have more
            predictions = predictions[:4]
        else:
            predictions = []
        
        # Add league logo to each prediction
        league = session.query(League).filter_by(league_id=team.league_id).first()
        league_logo = league.league_logo_path if league else None
        
        for pred in predictions:
            pred['league_logo'] = league_logo
        
        return jsonify(predictions), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

def get_next_four_weeks_matches(session, team_id, today):
    """Get the next 4 matches (max) for a team from today's date."""
    end_date = today + timedelta(days=28)  # 4 weeks from now
    
    # Get both home and away matches
    home_matches = session.query(Match).filter(
        Match.home_team_id == team_id,
        Match.date >= today,
        Match.date <= end_date,
        Match.is_played == False
    ).order_by(Match.date).all()
    
    away_matches = session.query(Match).filter(
        Match.away_team_id == team_id,
        Match.date >= today,
        Match.date <= end_date,
        Match.is_played == False
    ).order_by(Match.date).all()
    
    # Combine and sort by date
    all_matches = home_matches + away_matches
    all_matches.sort(key=lambda match: match.date)
    
    # Return only up to 4 matches
    return all_matches[:4]

def get_last_four_weeks_matches(session, team_id, today):
    """Get the last 4 matches for a team if no upcoming matches are found."""
    start_date = today - timedelta(days=28)  # 4 weeks ago
    
    # Get both home and away matches
    home_matches = session.query(Match).filter(
        Match.home_team_id == team_id,
        Match.date < today,
        Match.date >= start_date,
        Match.is_played == True
    ).order_by(Match.date.desc()).all()
    
    away_matches = session.query(Match).filter(
        Match.away_team_id == team_id,
        Match.date < today,
        Match.date >= start_date,
        Match.is_played == True
    ).order_by(Match.date.desc()).all()
    
    # Combine and sort by date (most recent first)
    all_matches = home_matches + away_matches
    all_matches.sort(key=lambda match: match.date, reverse=True)
    
    # Return only up to 4 matches
    return all_matches[:4]