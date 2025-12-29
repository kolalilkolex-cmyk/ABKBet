# App package
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.extensions import db

socketio = SocketIO()
jwt = JWTManager()


def create_app(config_name='development'):
    """Application factory pattern"""
    from config import config
    import os
    
    # Get the base directory (where app package is located)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS with specific settings for PythonAnywhere
    CORS(app, 
         resources={r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": False
         }})
    
    # Initialize SocketIO with fallback if Redis not available
    try:
        socketio.init_app(app, 
                         cors_allowed_origins="*",
                         message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'))
    except:
        # Fallback to simple mode without Redis
        socketio.init_app(app, cors_allowed_origins="*")
    
    return app

