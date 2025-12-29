from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import BookingCode, User
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import string
import json

booking_bp = Blueprint('booking', __name__, url_prefix='/api/booking')

def generate_booking_code(length=10):
    """Generate a random alphanumeric booking code"""
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        # Check if code already exists
        existing = BookingCode.query.filter_by(code=code).first()
        if not existing:
            return code

@booking_bp.route('/generate', methods=['POST'])
@jwt_required()
def create_booking_code():
    """Generate a booking code for a set of bet selections"""
    try:
        data = request.get_json()
        bet_data = data.get('bet_data')
        
        if not bet_data:
            return jsonify({'error': 'bet_data is required'}), 400
        
        # Validate bet_data is valid JSON
        try:
            if isinstance(bet_data, str):
                json.loads(bet_data)
            else:
                bet_data = json.dumps(bet_data)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid bet_data format'}), 400
        
        # Get current user
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        
        # Generate unique code
        code = generate_booking_code()
        
        # Create booking code record
        booking_code = BookingCode(
            code=code,
            bet_data=bet_data,
            created_by=user.id if user else None
        )
        
        db.session.add(booking_code)
        db.session.commit()
        
        return jsonify({
            'code': code,
            'bet_data': bet_data,
            'created_at': booking_code.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/<code>', methods=['GET'])
def get_booking_code(code):
    """Retrieve bet selections by booking code"""
    try:
        # Convert to uppercase for consistency
        code = code.upper()
        
        # Find booking code
        booking_code = BookingCode.query.filter_by(code=code).first()
        
        if not booking_code:
            return jsonify({'error': 'Booking code not found'}), 404
        
        # Increment used count
        booking_code.used_count += 1
        db.session.commit()
        
        return jsonify({
            'code': booking_code.code,
            'bet_data': booking_code.bet_data,
            'created_at': booking_code.created_at.isoformat(),
            'used_count': booking_code.used_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
