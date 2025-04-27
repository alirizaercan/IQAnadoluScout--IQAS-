# backend/controllers/match_analysis_controller.py
from flask import Blueprint, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import time
import json
import re

from services.video_analysis_service import VideoAnalysisService
from utils.database import Database
from models.match_analysis import MatchAnalysis
from models.football_team import FootballTeam

match_analysis_bp = Blueprint('match_analysis', __name__, url_prefix='/api/match-analysis')
db = Database()

# Define upload folder
UPLOAD_FOLDER = 'uploads/videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@match_analysis_bp.route('/analyze', methods=['POST'])
def analyze_match():
    """
    Upload and analyze match video
    Required form data:
    - video: Match video file
    - home_team: Home team name
    - away_team: Away team name
    - match_date: Match date (YYYY-MM-DD)
    """
    session = db.connect()
    try:
        # Check if video file is present
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        # Validate file type
        if not allowed_file(video_file.filename):
            return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get and validate other form data
        home_team = request.form.get('home_team')
        away_team = request.form.get('away_team')
        match_date_str = request.form.get('match_date')
        
        if not all([home_team, away_team, match_date_str]):
            return jsonify({'error': 'Missing required parameters: home_team, away_team, match_date'}), 400
        
        # Parse match date
        try:
            match_date = datetime.strptime(match_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Save video file
        timestamp = int(time.time())
        filename = secure_filename(f"{timestamp}_{video_file.filename}")
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(video_path)
        
        # Start analysis process
        video_analysis_service = VideoAnalysisService(session)
        analysis = video_analysis_service.analyze_video(video_path, home_team, away_team, match_date)
        
        return jsonify({
            'status': 'success',
            'message': 'Video analysis completed',
            'analysis_id': analysis.id,
            'home_team': analysis.home_team_name,
            'away_team': analysis.away_team_name,
            'match_date': analysis.match_date.strftime('%Y-%m-%d'),
            'processed_video_url': f'/api/match-analysis/{analysis.id}/video'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@match_analysis_bp.route('/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get match analysis data by ID"""
    session = db.connect()
    try:
        analysis = session.query(MatchAnalysis).filter_by(id=analysis_id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify({
            'id': analysis.id,
            'match_date': analysis.match_date.strftime('%Y-%m-%d'),
            'home_team': {
                'id': analysis.home_team_id,
                'name': analysis.home_team_name,
                'color': analysis.home_team_color
            },
            'away_team': {
                'id': analysis.away_team_id,
                'name': analysis.away_team_name,
                'color': analysis.away_team_color
            },
            'video_path': analysis.processed_video_path,
            'possession': {
                'home': round(analysis.home_possession_percentage, 2),
                'away': round(analysis.away_possession_percentage, 2)
            },
            'ball_control': {
                'home': round(analysis.home_ball_control_time, 2),
                'away': round(analysis.away_ball_control_time, 2)
            },
            'formations': {
                'home': analysis.home_formation,
                'away': analysis.away_formation
            },
            'statistics': {
                'speed': {
                    'home': round(analysis.home_avg_speed, 2),
                    'away': round(analysis.away_avg_speed, 2)
                },
                'distance': {
                    'home': round(analysis.home_total_distance, 2),
                    'away': round(analysis.away_total_distance, 2)
                },
                'attack_phases': {
                    'home': analysis.home_attack_phases,
                    'away': analysis.away_attack_phases
                }
            },
            'player_positions': {
                'home': json.loads(analysis.home_avg_player_positions) if analysis.home_avg_player_positions else {},
                'away': json.loads(analysis.away_avg_player_positions) if analysis.away_avg_player_positions else {}
            },
            'heatmaps': {
                'home': json.loads(analysis.home_heatmap) if analysis.home_heatmap else {},
                'away': json.loads(analysis.away_heatmap) if analysis.away_heatmap else {}
            },
            'key_moments': json.loads(analysis.key_moments) if analysis.key_moments else []
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@match_analysis_bp.route('/<int:analysis_id>/video', methods=['GET'])
def get_processed_video(analysis_id):
    session = db.connect()
    try:
        analysis = session.query(MatchAnalysis).filter_by(id=analysis_id).first()
        if not analysis or not analysis.processed_video_path:
            return jsonify({'error': 'Processed video not found'}), 404
        
        abs_path = os.path.abspath(analysis.processed_video_path)
        print(f"Trying to serve video from: {abs_path}")
        
        if not os.path.exists(abs_path):
            rel_path = os.path.join('uploads', 'processed_videos', os.path.basename(analysis.processed_video_path))
            abs_path = os.path.abspath(rel_path)
            
            if not os.path.exists(abs_path):
                return jsonify({'error': 'Video file not found'}), 404
        
        # Handle range requests
        range_header = request.headers.get('Range', None)
        if range_header:
            size = os.path.getsize(abs_path)
            byte1, byte2 = 0, None
            
            m = re.search('(\d+)-(\d*)', range_header)
            g = m.groups()
            
            if g[0]: byte1 = int(g[0])
            if g[1]: byte2 = int(g[1])
            
            length = size - byte1
            if byte2 is not None:
                length = byte2 - byte1 + 1
                
            data = None
            with open(abs_path, 'rb') as f:
                f.seek(byte1)
                data = f.read(length)
                
            rv = Response(data, 
                        206,
                        mimetype='video/mp4; codecs="avc1.42E01E, mp4a.40.2"',
                        direct_passthrough=True)
            rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
            rv.headers.add('Accept-Ranges', 'bytes')
            rv.headers.add('Content-Length', str(length))
            return rv
        
        return send_file(
            abs_path,
            mimetype='video/mp4; codecs="avc1.42E01E, mp4a.40.2"',
            conditional=True
        )
        
    except Exception as e:
        print(f"Error serving video: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
        
def file_sender(path, start, end):
    with open(path, 'rb') as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk_size = min(4096, remaining)
            chunk = f.read(chunk_size)
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk

@match_analysis_bp.route('/teams', methods=['GET'])
def get_teams():
    """Get list of available football teams"""
    session = db.connect()
    try:
        teams = session.query(FootballTeam).all()
        teams_list = [
            {
                'id': team.team_id,
                'name': team.team_name,
                'league': team.league_name,
                'img_path': team.img_path
            }
            for team in teams
        ]
        return jsonify({'teams': teams_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@match_analysis_bp.route('/recent', methods=['GET'])
def get_recent_analyses():
    """Get recent match analyses"""
    session = db.connect()
    try:
        limit = request.args.get('limit', 5, type=int)
        analyses = session.query(MatchAnalysis).order_by(MatchAnalysis.created_at.desc()).limit(limit).all()
        
        analyses_list = [
            {
                'id': analysis.id,
                'match_date': analysis.match_date.strftime('%Y-%m-%d'),
                'home_team': analysis.home_team_name,
                'away_team': analysis.away_team_name,
                'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for analysis in analyses
        ]
        
        return jsonify({'analyses': analyses_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()