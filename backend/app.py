# backend/app.py
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from controllers.auth_controller import auth_controller
from controllers.youth_dev_controller import youth_dev_controller
from controllers.physical_dev_controller import physical_bp as physical_controller

load_dotenv()

app = Flask(__name__, static_folder='frontend/build/static', template_folder='frontend/build')
CORS(app)

# Blueprint'i kayıt ediyoruz
app.register_blueprint(physical_controller, url_prefix='/api/physical-development')
app.register_blueprint(youth_dev_controller, url_prefix='/api/youth-development')
app.register_blueprint(auth_controller, url_prefix='/api/auth')


@app.route('/')
def home():
    return "Welcome to the IQAnadoluScout API!"

@app.route('/<path:path>')
def serve_react_app(path):
    return send_from_directory(app.template_folder, path)

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)