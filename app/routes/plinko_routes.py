"""
Plinko Game Routes
Drop ball through pegs for multipliers
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Bet, Transaction, BetStatus
import random
import hashlib
import secrets
from datetime import datetime
from decimal import Decimal

plinko_bp = Blueprint('plinko', __name__, url_prefix='/api/plinko')

# Plinko multipliers for different risk levels
# 16 rows, 17 buckets
MULTIPLIERS = {
    'low': [1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 1.0, 0.9, 1.0, 0.9, 1.0, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
    'medium': [5.6, 2.1, 1.1, 1.0, 0.5, 0.3, 1.0, 0.7, 0.4, 0.7, 1.0, 0.3, 0.5, 1.0, 1.1, 2.1, 5.6],
    'high': [33.0, 11.0, 4.0, 2.0, 1.1, 1.0, 0.5, 0.2, 0.1, 0.2, 0.5, 1.0, 1.1, 2.0, 4.0, 11.0, 33.0]
}

def generate_plinko_path(server_seed, client_seed, rows=16):
    """Generate provably fair plinko path"""
    combined = f"{server_seed}{client_seed}"
    hash_result = hashlib.sha256(combined.encode()).hexdigest()
    
    # Each row, ball can go left (L) or right (R)
    path = []
    position = 8  # Start at center (middle of 17 buckets: 0-16, so center is 8)
    
    for i in range(rows):
        # Use 2 bits of hash for each row
        bit_index = i * 2
        hash_bits = hash_result[bit_index:bit_index+2]
        direction = int(hash_bits, 16) % 2  # 0 = left, 1 = right
        
        if direction == 1:
            position += 1  # Move right
            path.append('R')
        else:
            position -= 1  # Move left
            path.append('L')
    
    # Final bucket is the position, clamped to valid range
    # Ensure position is within 0 to 16 (17 buckets)
    bucket = max(0, min(position, len(MULTIPLIERS['low']) - 1))
    
    return path, bucket

@plinko_bp.route('/drop', methods=['POST'])
@jwt_required()
def drop_ball():
    """Drop a plinko ball"""
    user_id = get_jwt_identity()
    data = request.json
    
    amount = float(data.get('amount', 0))
    risk = data.get('risk', 'medium')  # low, medium, high
    
    if amount <= 0:
        return jsonify({'error': 'Invalid bet amount'}), 400
    
    if risk not in ['low', 'medium', 'high']:
        return jsonify({'error': 'Risk must be low, medium, or high'}), 400
    
    # Check user balance
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.balance < Decimal(str(amount)):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Generate provably fair result
    server_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()
    client_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
    
    path, bucket = generate_plinko_path(server_seed, client_seed)
    multiplier = MULTIPLIERS[risk][bucket]
    
    # Calculate winnings
    bet_amount = Decimal(str(amount))
    winnings = bet_amount * Decimal(str(multiplier))
    
    # Deduct bet first, then add winnings
    user.balance -= float(amount)
    user.balance += float(winnings)
    profit = winnings - bet_amount
    
    # Determine status
    if winnings > bet_amount:
        status = BetStatus.WON
    elif winnings < bet_amount:
        status = BetStatus.LOST
    else:
        status = BetStatus.VOIDED
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'path': path,
        'bucket': bucket,
        'multiplier': multiplier,
        'amount': amount,
        'winnings': float(winnings),
        'profit': float(profit),
        'new_balance': float(user.balance),
        'server_seed': server_seed,
        'client_seed': client_seed
    })

@plinko_bp.route('/multipliers', methods=['GET'])
def get_multipliers():
    """Get multipliers for all risk levels"""
    return jsonify({
        'multipliers': MULTIPLIERS
    })

@plinko_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's plinko history"""
    user_id = get_jwt_identity()
    
    bets = Bet.query.filter_by(
        user_id=user_id,
        bet_type='plinko'
    ).order_by(Bet.created_at.desc()).limit(50).all()
    
    history = []
    for bet in bets:
        history.append({
            'id': bet.id,
            'amount': float(bet.stake),
            'multiplier': float(bet.odds),
            'description': bet.description,
            'status': bet.status,
            'created_at': bet.created_at.isoformat()
        })
    
    return jsonify({'history': history})
