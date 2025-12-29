"""
Simplified ABKBet Flask application that works with Python 3.14
Uses JSON storage instead of SQLAlchemy until we can fix the database
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize extensions
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'ABKBet API is running!'}), 200

# Test endpoint
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Flask is working!',
        'python_version': '3.14',
        'flask_version': '3.1.2'
    }), 200

# Simple welcome endpoint
@app.route('/', methods=['GET'])
def welcome():
    return jsonify({
        'application': 'ABKBet - Bitcoin Betting Platform',
        'status': 'running',
        'available_endpoints': {
            'health': '/api/health',
            'test': '/api/test'
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════╗
    ║     ABKBet - Bitcoin Betting Platform  ║
    ║          Flask 3.1.2 Running           ║
    ╚════════════════════════════════════════╝
    
    Server starting...
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
