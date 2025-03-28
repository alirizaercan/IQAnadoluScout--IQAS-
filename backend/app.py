# backend/app.py
import os
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from controllers.auth_controller import auth_controller
from controllers.youth_dev_controller import youth_dev_controller
from controllers.physical_dev_controller import physical_bp as physical_controller
from controllers.conditional_dev_controller import conditional_bp as conditional_controller
from controllers.endurance_dev_controller import endurance_bp as endurance_controller
from controllers.scouting_controller import scouting_bp as scouting_controller
from controllers.transfer_controller import transfer_bp as transfer_controller
from controllers.performance_controller import performance_bp as performance_controller

load_dotenv()

app = Flask(__name__, 
            static_folder='static', 
            template_folder='frontend/build')


# CORS yapılandırmasını güncelledik, tüm domainlerden gelen isteklere izin veriyoruz
CORS(app, origins="*")

# Blueprint'i kayıt ediyoruz
app.register_blueprint(physical_controller, url_prefix='/api/physical-development')
app.register_blueprint(conditional_controller, url_prefix='/api/conditional-development')
app.register_blueprint(endurance_controller, url_prefix='/api/endurance-development')
app.register_blueprint(youth_dev_controller, url_prefix='/api/youth-development')
app.register_blueprint(scouting_controller, url_prefix='/api/scouting')
app.register_blueprint(transfer_controller, url_prefix='/api/transfer')
app.register_blueprint(performance_controller, url_prefix='/api/performance')
app.register_blueprint(auth_controller, url_prefix='/api/auth')

@app.route('/')
def home():
    return "Welcome to the IQAnadoluScout API!"

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


@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
