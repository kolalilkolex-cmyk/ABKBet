"""
Dice Game Routes
Roll dice and predict over/under target number
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

dice_bp = Blueprint('dice', __name__, url_prefix='/api/dice')

def generate_dice_result(client_seed, server_seed, nonce):
    """Generate provably fair dice result (0.00 - 99.99)"""
    combined = f"{server_seed}{client_seed}{nonce}"
    hash_result = hashlib.sha256(combined.encode()).hexdigest()
    
    # Convert first 8 hex chars to number 0-99.99
    hash_int = int(hash_result[:8], 16)
    result = (hash_int % 10000) / 100.0
    
    return round(result, 2)

@dice_bp.route('/roll', methods=['POST'])
@jwt_required()
def roll_dice():
    """Roll the dice"""
    user_id = get_jwt_identity()
    data = request.json
    
    amount = float(data.get('amount', 0))
    target = float(data.get('target', 50))
    prediction = data.get('prediction', 'over')  # 'over' or 'under'
    
    if amount <= 0:
        return jsonify({'error': 'Invalid bet amount'}), 400
    
    if target < 1 or target > 98:
        return jsonify({'error': 'Target must be between 1 and 98'}), 400
    
    if prediction not in ['over', 'under']:
        return jsonify({'error': 'Prediction must be over or under'}), 400
    
    # Check user balance
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.balance < Decimal(str(amount)):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Generate provably fair result
    server_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()
    client_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
    nonce = int(datetime.utcnow().timestamp() * 1000)
    
    result = generate_dice_result(client_seed, server_seed, nonce)
    
    # Calculate if win
    won = False
    if prediction == 'over' and result > target:
        won = True
    elif prediction == 'under' and result < target:
        won = True
    
    # Calculate payout
    # Formula: multiplier = 99 / (100 - target) for over
    #          multiplier = 99 / target for under
    if prediction == 'over':
        multiplier = 99.0 / (100 - target)
    else:
        multiplier = 99.0 / target
    
    multiplier = round(multiplier, 2)
    
    bet_amount = Decimal(str(amount))
    
    if won:
        winnings = bet_amount * Decimal(str(multiplier))
        profit = winnings - bet_amount
        user.balance += float(profit)  # Only add profit (bet was already deducted)
        
        status = BetStatus.WON
    else:
        user.balance -= float(bet_amount)
        winnings = Decimal('0')
        profit = -bet_amount
        
        status = BetStatus.LOST
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'result': result,
        'target': target,
        'prediction': prediction,
        'won': won,
        'multiplier': multiplier,
        'amount': amount,
        'winnings': float(winnings) if won else 0,
        'profit': float(profit),
        'new_balance': float(user.balance),
        'server_seed': server_seed,
        'client_seed': client_seed,
        'nonce': nonce
    })

@dice_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's dice history"""
    user_id = get_jwt_identity()
    
    bets = Bet.query.filter_by(
        user_id=user_id,
        bet_type='dice'
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
