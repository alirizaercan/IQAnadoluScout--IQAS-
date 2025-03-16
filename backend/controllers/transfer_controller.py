from flask import Blueprint, request, jsonify
from services.transfer_service import TransferService
from utils.database import Database

transfer_bp = Blueprint('transfer', __name__)
db = Database()

@transfer_bp.route('/market-value-range', methods=['GET'])
def get_market_value_range():
    """Get minimum and maximum market values from all footballers."""
    session = db.connect()
    try:
        service = TransferService(session)
        value_range = service.get_market_value_range()
        return jsonify(value_range), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/players-by-budget', methods=['GET'])
def get_players_by_budget():
    """Get players who fit within the specified budget."""
    budget = request.args.get('budget', type=float)
    limit = request.args.get('limit', default=200, type=int)
    
    if not budget:
        return jsonify({'error': 'Budget parameter is required'}), 400
    
    session = db.connect()
    try:
        service = TransferService(session)
        players = service.get_players_by_budget(budget, limit)
        return jsonify(players), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/filtered-players', methods=['GET'])
def get_filtered_players():
    """Get players filtered by various criteria."""
    budget = request.args.get('budget', type=float)
    position = request.args.get('position')
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    min_rating = request.args.get('min_rating', type=float)
    limit = request.args.get('limit', default=200, type=int)
    
    session = db.connect()
    try:
        service = TransferService(session)
        players = service.get_filtered_players(
            budget=budget, 
            position=position, 
            min_age=min_age, 
            max_age=max_age, 
            min_rating=min_rating, 
            limit=limit
        )
        return jsonify(players), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/player-details/<int:footballer_id>', methods=['GET'])
def get_player_details(footballer_id):
    """Get detailed information about a player."""
    session = db.connect()
    try:
        service = TransferService(session)
        player_details = service.get_player_details(footballer_id)
        if not player_details:
            return jsonify({'message': 'Player not found'}), 404
        return jsonify(player_details), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/similar-players/<int:footballer_id>', methods=['GET'])
def get_similar_players(footballer_id):
    """Find similar players based on attributes."""
    limit = request.args.get('limit', default=10, type=int)
    
    session = db.connect()
    try:
        service = TransferService(session)
        similar_players = service.get_similar_players(footballer_id, limit)
        return jsonify(similar_players), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/dashboard-data', methods=['GET'])
def get_transfer_dashboard_data():
    """Get data for the transfer dashboard."""
    session = db.connect()
    try:
        service = TransferService(session)
        dashboard_data = service.get_transfer_dashboard_data()
        return jsonify(dashboard_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/leagues', methods=['GET'])
def get_all_leagues():
    """Get all leagues."""
    session = db.connect()
    try:
        service = TransferService(session)
        leagues = service.get_all_leagues()
        return jsonify(leagues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/teams', methods=['GET'])
def get_all_teams():
    """Get all teams."""
    session = db.connect()
    try:
        service = TransferService(session)
        teams = service.get_all_teams()
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/teams/league/<int:league_id>', methods=['GET'])
def get_teams_by_league(league_id):
    """Get all teams in a specific league."""
    session = db.connect()
    try:
        service = TransferService(session)
        teams = service.get_teams_by_league(league_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/team/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
    """Get team details by team_id."""
    session = db.connect()
    try:
        service = TransferService(session)
        team = service.get_team_by_id(team_id)
        if not team:
            return jsonify({'message': 'Team not found'}), 404
        return jsonify(team), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@transfer_bp.route('/team/players/<int:team_id>', methods=['GET'])
def get_team_players(team_id):
    """Get all player data for a specific team."""
    session = db.connect()
    try:
        service = TransferService(session)
        players = service.get_team_players_data(team_id)
        return jsonify(players), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)