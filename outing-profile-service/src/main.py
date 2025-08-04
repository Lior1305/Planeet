import logging
from flask import Flask
from flask_cors import CORS
from .database import db
from .routes import api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.connect()
    
    # Register blueprints
    app.register_blueprint(api)
    
    return app

if __name__ == '__main__':
    logger.info("Starting Outing Profile Server...")
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 