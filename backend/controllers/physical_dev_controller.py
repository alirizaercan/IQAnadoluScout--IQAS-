# backend/controllers/physical_dev_controller.py
from flask import Blueprint, request, jsonify
from services.physical_service import PhysicalService
from utils.database import Database

physical_bp = Blueprint('physical_dev', __name__)
db = Database()

@physical_bp.route('/leagues', methods=['GET'])
def get_leagues():
    """Get all leagues."""
    print("GET request received at /api/physical-development/leagues")  # Debugging line
    session = db.connect()
    try:
        service = PhysicalService(session)
        leagues = service.get_all_leagues()
        if not leagues:
            return jsonify({'message': 'No leagues found'}), 404  # Return a clear message if no leagues found
        return jsonify(leagues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@physical_bp.route('/teams/<league_id>', methods=['GET'])
def get_teams(league_id):
    """Get teams by league_id."""
    session = db.connect()
    try:
        service = PhysicalService(session)
        teams = service.get_teams_by_league(league_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@physical_bp.route('/footballers/<team_id>', methods=['GET'])
def get_footballers(team_id):
    """Get footballers by team_id."""
    session = db.connect()
    try:
        service = PhysicalService(session)
        footballers = service.get_footballers_by_team(team_id)
        return jsonify(footballers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@physical_bp.route('/physical-data', methods=['POST'])
def get_physical_data():
    """Get physical data for a footballer within a date range."""
    session = db.connect()
    data = request.json
    try:
        footballer_id = data.get('footballer_id')
        graph_type = data.get('graph_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        service = PhysicalService(session)
        graph_data = service.get_physical_data(footballer_id, graph_type, start_date, end_date)
        return jsonify(graph_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)
