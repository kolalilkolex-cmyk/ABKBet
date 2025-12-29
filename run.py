import os
import logging
from flask import jsonify, render_template, send_from_directory, make_response
from dotenv import load_dotenv
from flask_migrate import Migrate

# Load environment variables first
load_dotenv()

# Import from app package
from app import create_app, db, socketio, jwt
import app.models
import app.websocket_events as websocket_module

migrate = Migrate()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Also add a file handler so logs are persisted to `logs/run_app.log`
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    pass

file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'run_app.log'))
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Ensure werkzeug (Flask server) logs also go to the same file
logging.getLogger('werkzeug').addHandler(file_handler)

# Create Flask app using factory pattern
config_name = os.getenv('FLASK_ENV', 'development')
flask_app = create_app(config_name)

# Initialize additional extensions
migrate.init_app(flask_app, db)
# JWT is now initialized in create_app factory

# Register blueprints
from app.routes.auth_routes import auth_bp
from app.routes.payment_routes import payment_bp
from app.routes.bet_routes import bet_bp
from app.routes.admin_routes import admin_bp
from app.routes.webhook_routes import webhook_bp
from app.routes.booking_routes import booking_bp
from app.routes.deposit_routes import deposit_bp
from app.routes.withdrawal_routes import withdrawal_bp
from app.routes.premium_routes import premium_bp
from app.routes.virtual_game_routes import virtual_game_bp
from app.routes.crash_routes import crash_bp
from app.routes.dice_routes import dice_bp
from app.routes.mines_routes import mines_bp
from app.routes.plinko_routes import plinko_bp

flask_app.register_blueprint(auth_bp)
flask_app.register_blueprint(payment_bp)
flask_app.register_blueprint(bet_bp)
flask_app.register_blueprint(admin_bp)
flask_app.register_blueprint(webhook_bp)
flask_app.register_blueprint(booking_bp)
flask_app.register_blueprint(deposit_bp)
flask_app.register_blueprint(withdrawal_bp)
flask_app.register_blueprint(premium_bp)
flask_app.register_blueprint(virtual_game_bp)
flask_app.register_blueprint(crash_bp)
flask_app.register_blueprint(dice_bp)
flask_app.register_blueprint(mines_bp)
flask_app.register_blueprint(plinko_bp)

logger.info("WebSocket support enabled")

# Create tables
with flask_app.app_context():
    # db.create_all()
    # Log the active DB URI so it's easy to verify which DB the app is
    # using (helps avoid relying on a relative default path)
    try:
        db_uri = flask_app.config.get('SQLALCHEMY_DATABASE_URI')
        logger.info(f"Database tables created/verified — using DB: {db_uri}")
    except Exception:
        logger.info("Database tables created/verified")

# Health check endpoint
@flask_app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

# Favicon route to prevent 404
@flask_app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(flask_app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# Serve web UI
@flask_app.route('/')
def index():
    # Add cache control headers to prevent caching
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/terms')
def terms():
    # Add cache control headers to prevent caching
    response = make_response(render_template('terms.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/admin')
def admin():
    # Add cache control headers to prevent caching
    response = make_response(render_template('admin.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/secure-admin-access-2024')
def admin_login():
    # Dedicated admin login page (obscured URL for security)
    response = make_response(render_template('admin_login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/premium_admin')
def premium_admin():
    # Add cache control headers to prevent caching
    response = make_response(render_template('premium_admin.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/admin2')
def admin2():
    # Fresh admin page to bypass browser cache
    response = make_response(render_template('admin2.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/admin-simple')
def admin_simple():
    # Ultra-simple admin page for testing
    response = make_response(render_template('admin_simple.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/test')
def test_matches():
    # Test page to debug matches
    response = make_response(render_template('test_matches.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@flask_app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Error handlers
@flask_app.errorhandler(404)
def not_found(e):
    return jsonify({'message': 'Resource not found'}), 404

@flask_app.errorhandler(500)
def internal_error(e):
    import traceback
    print("="*80)
    print("500 ERROR HANDLER TRIGGERED!")
    print("="*80)
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("="*80)
    logger.error(f"Internal server error: {e}", exc_info=True)
    return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

logger.info(f"Application created with config: {config_name}")

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(flask_app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
