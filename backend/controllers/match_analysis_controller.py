# backend/controllers/match_analysis_controller.py
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from services.video_analysis_service import VideoAnalysisService
from utils.database import Database
from models.match_analysis import MatchAnalysis

match_analysis_bp = Blueprint('match_analysis', __name__)
db = Database()

# Configuration
UPLOAD_FOLDER = 'uploads/videos'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@match_analysis_bp.route('/analyze', methods=['POST'])
def analyze_video():
    # Check if files are present
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400
    
    video_file = request.files['video']
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    match_date = request.form.get('match_date')
    
    if not all([video_file, home_team, away_team, match_date]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if video_file.filename == '':
        return jsonify({'error': 'No selected video file'}), 400
    
    if not allowed_file(video_file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Create upload directory if not exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save the video file
        filename = secure_filename(f"{datetime.now().timestamp()}_{video_file.filename}")
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(video_path)
        
        # Parse date
        match_date_obj = datetime.strptime(match_date, '%Y-%m-%d').date()
        
        # Analyze video
        analyzer = VideoAnalysisService()
        analysis = analyzer.analyze_video(video_path, home_team, away_team, match_date_obj)
        
        return jsonify({
            'message': 'Analysis completed',
            'analysis_id': analysis.id,
            'home_possession': analysis.home_possession_percentage,
            'away_possession': analysis.away_possession_percentage,
            'home_formation': analysis.home_formation,
            'away_formation': analysis.away_formation
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@match_analysis_bp.route('/results/<int:analysis_id>', methods=['GET'])
def get_analysis_results(analysis_id):
    session = db.connect()
    try:
        analysis = session.query(MatchAnalysis).filter_by(id=analysis_id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify({
            'id': analysis.id,
            'match_date': str(analysis.match_date),
            'home_team_id': analysis.home_team_id,
            'away_team_id': analysis.away_team_id,
            'home_possession': analysis.home_possession_percentage,
            'away_possession': analysis.away_possession_percentage,
            'home_pass_accuracy': analysis.home_pass_accuracy,
            'away_pass_accuracy': analysis.away_pass_accuracy,
            'home_shots': analysis.home_shots,
            'away_shots': analysis.away_shots,
            'home_shots_on_target': analysis.home_shots_on_target,
            'away_shots_on_target': analysis.away_shots_on_target,
            'home_formation': analysis.home_formation,
            'away_formation': analysis.away_formation,
            'home_formation_changes': analysis.home_formation_changes,
            'away_formation_changes': analysis.away_formation_changes,
            'home_heatmap': analysis.home_heatmap,
            'away_heatmap': analysis.away_heatmap,
            'possession_timeline': analysis.possession_timeline,
            'formation_changes': analysis.formation_changes
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close(session)