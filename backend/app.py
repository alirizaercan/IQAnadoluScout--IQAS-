# backend/app.py
import os
import logging
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.serving import WSGIRequestHandler
from controllers.auth_controller import auth_controller
from controllers.youth_dev_controller import youth_dev_controller
from controllers.physical_dev_controller import physical_bp as physical_controller
from controllers.conditional_dev_controller import conditional_bp as conditional_controller
from controllers.endurance_dev_controller import endurance_bp as endurance_controller
from controllers.scouting_controller import scouting_bp as scouting_controller
from controllers.transfer_controller import transfer_bp as transfer_controller
from controllers.performance_controller import performance_bp as performance_controller
from controllers.score_prediction_controller import match_bp as score_prediction_controller
from controllers.match_analysis_controller import match_analysis_bp

# Import all models to register them with SQLAlchemy
# This ensures the models are loaded before they're used
import models.football_team
import models.user
import models.footballer
import models.league
import models.match
import models.notification  # Add this import

# Log ayarlarını yapılandır
#logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Sadece warning ve üstü logları göster
#WSGIRequestHandler.log = lambda *args, **kwargs: None  # WSGI request loglarını kapat

load_dotenv()

app = Flask(__name__, 
            static_folder='static', 
            template_folder='frontend/build')

CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Takım logolarının bulunduğu klasörü oluştur
team_logos_dir = os.path.join(app.static_folder, 'team-logos')
os.makedirs(team_logos_dir, exist_ok=True)

# Blueprint'i kayıt ediyoruz
app.register_blueprint(physical_controller, url_prefix='/api/physical-development')
app.register_blueprint(conditional_controller, url_prefix='/api/conditional-development')
app.register_blueprint(endurance_controller, url_prefix='/api/endurance-development')
app.register_blueprint(youth_dev_controller, url_prefix='/api/youth-development')
app.register_blueprint(scouting_controller, url_prefix='/api/scouting')
app.register_blueprint(transfer_controller, url_prefix='/api/transfer')
app.register_blueprint(performance_controller, url_prefix='/api/performance')
app.register_blueprint(score_prediction_controller, url_prefix='/api/match-score-prediction')
app.register_blueprint(auth_controller, url_prefix='/api/auth')
app.register_blueprint(match_analysis_bp, url_prefix='/api/match-analysis')

@app.route('/')
def home():
    return "Welcome to the TYFOR API!"

@app.route('/<path:path>')
def serve_react_app(path):
    return send_from_directory(app.template_folder, path)


@app.route('/static/graphs/physical_graphs/<path:filename>')
def serve_physical_graph(filename):
    graphs_dir = os.path.join(app.root_path, 'static', 'graphs', 'physical_graphs')
    return send_from_directory(graphs_dir, filename)

@app.route('/static/graphs/conditional_graphs/<path:filename>')
def serve_conditional_graph(filename):
    graphs_dir = os.path.join(app.root_path, 'static', 'graphs', 'conditional_graphs')
    return send_from_directory(graphs_dir, filename)

@app.route('/static/graphs/endurance_graphs/<path:filename>')
def serve_endurance_graph(filename):
    graphs_dir = os.path.join(app.root_path, 'static', 'graphs', 'endurance_graphs')
    return send_from_directory(graphs_dir, filename)

@app.route('/static/graphs/performance_graphs/<path:filename>')
def serve_performance_graph(filename):
    graphs_dir = os.path.join(app.root_path, 'static', 'graphs', 'performance_graphs')
    return send_from_directory(graphs_dir, filename)

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory('uploads', filename)

@app.route('/uploads/processed_videos/<path:filename>')
def serve_processed_videos(filename):
    videos_dir = os.path.join(app.root_path, 'uploads', 'processed_videos')
    return send_from_directory(videos_dir, filename)

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
