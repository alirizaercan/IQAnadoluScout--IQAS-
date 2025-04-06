# backend/controllers/score_prediction_controller.py
from flask import Blueprint, request, jsonify
from services.match_service import MatchService
from utils.database import Database

match_bp = Blueprint('match_score', __name__)
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
        service = MatchService(session)
        predictions = service.predict_match_scores(team_id)
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)