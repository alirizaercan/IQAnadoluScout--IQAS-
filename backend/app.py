import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from controllers.auth_controller import AuthController

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__, static_folder='frontend/build/static', template_folder='frontend/build')

# Enable CORS to allow requests from the frontend (React)
CORS(app)

# Register the AuthController blueprint
auth_controller = AuthController()
app.register_blueprint(auth_controller.auth_controller, url_prefix='/api/auth')

# Health check route
@app.route('/')
def home():
    return "Welcome to the IQAnadoluScout API!"

# Serve React's built index.html for frontend route
@app.route('/<path:path>')
def serve_react_app(path):
    # Serve any files in the static folder
    return send_from_directory(app.template_folder, path)

@app.route('/')
def index():
    # Serve the React frontend
    return send_from_directory(app.template_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)

