from flask import Blueprint, request, jsonify
from services.player_service import PlayerService
from utils.database import Database

scouting_bp = Blueprint('scouting_network', __name__)
db = Database()

@scouting_bp.route('/leagues', methods=['GET'])
def get_all_leagues():
    """Get all leagues."""
    session = db.connect()
    try:
        service = PlayerService(session)
        leagues = service.get_all_leagues()
        return jsonify(leagues), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/teams', methods=['GET'])
def get_all_teams():
    """Get all teams."""
    session = db.connect()
    try:
        service = PlayerService(session)
        teams = service.get_all_teams()
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/teams/league/<int:league_id>', methods=['GET'])
def get_teams_by_league(league_id):
    """Get all teams in a specific league."""
    session = db.connect()
    try:
        service = PlayerService(session)
        teams = service.get_teams_by_league(league_id)
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/team/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
    """Get team details by team_id."""
    session = db.connect()
    try:
        service = PlayerService(session)
        team = service.get_team_by_id(team_id)
        if not team:
            return jsonify({'message': 'Team not found'}), 404
        return jsonify(team), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/footballers/team/<int:team_id>', methods=['GET'])
def get_footballers_by_team(team_id):
    """Get all footballers in a specific team."""
    session = db.connect()
    try:
        service = PlayerService(session)
        footballers = service.get_footballers_by_team(team_id)
        return jsonify(footballers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/player/<int:player_id>', methods=['GET'])
def get_player_by_id(player_id):
    """Get player details by player_id."""
    session = db.connect()
    try:
        service = PlayerService(session)
        player = service.get_player_by_id(player_id)
        if not player:
            return jsonify({'message': 'Player not found'}), 404
        # Convert SQLAlchemy object to dictionary
        player_dict = {column.name: getattr(player, column.name) 
                      for column in player.__table__.columns}
        return jsonify(player_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/players/footballer/<int:footballer_id>', methods=['GET'])
def get_players_by_footballer_id(footballer_id):
    """Get all player records for a specific footballer."""
    session = db.connect()
    try:
        service = PlayerService(session)
        players = service.get_players_by_footballer_id(footballer_id)
        # Convert SQLAlchemy objects to dictionaries
        players_dict = [{column.name: getattr(player, column.name) 
                        for column in player.__table__.columns} 
                        for player in players]
        return jsonify(players_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/team/players/<int:team_id>', methods=['GET'])
def get_team_players(team_id):
    """Get all player data for a specific team."""
    session = db.connect()
    try:
        service = PlayerService(session)
        players = service.get_team_players_data(team_id)
        return jsonify(players), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/team/positions/<int:team_id>', methods=['GET'])
def get_player_positions(team_id):
    """Get position distribution for a team."""
    session = db.connect()
    try:
        service = PlayerService(session)
        positions = service.get_player_positions(team_id)
        return jsonify(positions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/team/critical-positions/<int:team_id>', methods=['GET'])
def find_critical_positions(team_id):
    """Find critical positions that need reinforcement for a team."""
    session = db.connect()
    try:
        service = PlayerService(session)
        critical_positions = service.find_critical_positions(team_id)
        return jsonify(critical_positions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/recommend', methods=['POST'])
def recommend_players():
    """Recommend players for a specific position based on team needs."""
    data = request.json
    team_id = data.get('team_id')
    position = data.get('position')
    
    if not team_id or not position:
        return jsonify({'error': 'Team ID and position are required'}), 400
    
    session = db.connect()
    try:
        service = PlayerService(session)
        recommendations = service.recommend_players(team_id, position)
        return jsonify(recommendations), 200
    except Exception as e:
        print(f"Error in recommend_players: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/team/needs/<int:team_id>', methods=['GET'])
def recommend_players_by_team_needs(team_id):
    """Recommend players based on team's critical position needs."""
    session = db.connect()
    try:
        service = PlayerService(session)
        recommendations = service.recommend_players_by_team_needs(team_id)
        return jsonify(recommendations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/team/recommendation-summary/<int:team_id>', methods=['GET'])
def get_team_recommendation_summary(team_id):
    """Get a summary of team needs and player recommendations."""
    session = db.connect()
    try:
        service = PlayerService(session)
        summary = service.get_team_recommendation_summary(team_id)
        if 'status' in summary and summary['status'] == 'error':
            return jsonify(summary), 404
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/player/calculate-score', methods=['POST'])
def calculate_player_score():
    """Calculate a player's score for a specific position."""
    data = request.json
    player_data = data.get('player_data', {})
    position = data.get('position')
    
    if not player_data or not position:
        return jsonify({'error': 'Player data and position are required'}), 400
    
    session = db.connect()
    try:
        service = PlayerService(session)
        score = service.calculate_player_score(player_data, position)
        return jsonify({'score': score}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/position-mapping', methods=['GET'])
def get_position_mapping():
    """Get position mapping for standardization."""
    session = db.connect()
    try:
        service = PlayerService(session)
        return jsonify(service.position_mapping), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)
        
@scouting_bp.route('/ideal-distribution', methods=['GET'])
def get_ideal_distribution():
    """Get ideal position distribution for team balance."""
    session = db.connect()
    try:
        service = PlayerService(session)
        return jsonify(service.ideal_position_distribution), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/position-features', methods=['GET'])
def get_position_features():
    """Get position feature mapping for player recommendations."""
    session = db.connect()
    try:
        service = PlayerService(session)
        return jsonify(service.position_features), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/compare-players', methods=['POST'])
def compare_players():
    """Compare multiple players based on their attributes."""
    data = request.json
    player_ids = data.get('player_ids', [])
    
    if not player_ids or not isinstance(player_ids, list):
        return jsonify({'error': 'A list of player IDs is required'}), 400
    
    session = db.connect()
    try:
        service = PlayerService(session)
        players_data = []
        
        for player_id in player_ids:
            player = service.get_player_by_id(player_id)
            if player:
                # Convert SQLAlchemy object to dictionary
                player_dict = {column.name: getattr(player, column.name) 
                              for column in player.__table__.columns}
                players_data.append(player_dict)
        
        if not players_data:
            return jsonify({'message': 'No players found with provided IDs'}), 404
            
        return jsonify(players_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)

@scouting_bp.route('/team/scouting-report/<int:team_id>', methods=['GET'])
def get_team_scouting_report(team_id):
    """Get a comprehensive scouting report for a team."""
    session = db.connect()
    try:
        service = PlayerService(session)
        # Get team details
        team = service.get_team_by_id(team_id)
        if not team:
            return jsonify({'message': 'Team not found'}), 404
            
        # Get critical positions
        critical_positions = service.find_critical_positions(team_id)
        
        # Get recommendations for top critical position
        recommendations = []
        if critical_positions:
            top_position = critical_positions[0]['position']
            recommendations = service.recommend_players(team_id, top_position)
            
        # Get position distribution
        positions = service.get_player_positions(team_id)
        
        # Create scouting report
        report = {
            'team': team,
            'critical_positions': critical_positions,
            'position_distribution': positions,
            'recommendations': recommendations
        }
        
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)