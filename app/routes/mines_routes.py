"""
Mines Game Routes
Grid-based game - reveal gems, avoid mines
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

mines_bp = Blueprint('mines', __name__, url_prefix='/api/mines')

# Active games storage
active_games = {}

def generate_mine_positions(server_seed, client_seed, num_mines):
    """Generate provably fair mine positions"""
    combined = f"{server_seed}{client_seed}"
    hash_result = hashlib.sha256(combined.encode()).hexdigest()
    
    positions = []
    for i in range(num_mines):
        # Use different parts of hash for each mine
        hash_part = hash_result[i*4:(i+1)*4]
        position = int(hash_part, 16) % 25  # 5x5 grid
        
        # Ensure unique positions
        while position in positions:
            position = (position + 1) % 25
        
        positions.append(position)
    
    return positions

def calculate_multiplier(revealed, total_tiles, num_mines):
    """Calculate current multiplier based on revealed tiles"""
    safe_tiles = total_tiles - num_mines
    if revealed == 0:
        return 1.0
    
    # Progressive multiplier
    multiplier = 1.0
    for i in range(revealed):
        multiplier *= (total_tiles - i) / (safe_tiles - i)
    
    return round(multiplier, 2)

@mines_bp.route('/start', methods=['POST'])
@jwt_required()
def start_game():
    """Start a new mines game"""
    user_id = get_jwt_identity()
    data = request.json
    
    amount = float(data.get('amount', 0))
    num_mines = int(data.get('mines', 3))
    
    if amount <= 0:
        return jsonify({'error': 'Invalid bet amount'}), 400
    
    if num_mines < 1 or num_mines > 24:
        return jsonify({'error': 'Mines must be between 1 and 24'}), 400
    
    # Check user balance
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.balance < Decimal(str(amount)):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Deduct balance
    user.balance -= float(amount)
    db.session.commit()
    
    # Generate mine positions
    server_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()
    client_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
    mine_positions = generate_mine_positions(server_seed, client_seed, num_mines)
    
    game_id = f"{user_id}_{int(datetime.utcnow().timestamp() * 1000)}"
    
    # Store game state
    active_games[game_id] = {
        'user_id': user_id,
        'amount': amount,
        'num_mines': num_mines,
        'mine_positions': mine_positions,
        'revealed': [],
        'status': 'active',
        'server_seed': server_seed,
        'client_seed': client_seed
    }
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'num_mines': num_mines,
        'amount': amount,
        'new_balance': float(user.balance)
    })

@mines_bp.route('/reveal', methods=['POST'])
@jwt_required()
def reveal_tile():
    """Reveal a tile"""
    user_id = get_jwt_identity()
    data = request.json
    
    game_id = data.get('game_id')
    position = int(data.get('position'))
    
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = active_games[game_id]
    
    if game['user_id'] != user_id:
        return jsonify({'error': 'Not your game'}), 403
    
    if game['status'] != 'active':
        return jsonify({'error': 'Game is not active'}), 400
    
    if position in game['revealed']:
        return jsonify({'error': 'Tile already revealed'}), 400
    
    # Check if mine
    is_mine = position in game['mine_positions']
    
    if is_mine:
        # Hit a mine - game over
        game['status'] = 'lost'
        game['revealed'].append(position)
        
        # Balance already deducted when game started
        user = User.query.get(user_id)
        
        return jsonify({
            'success': True,
            'is_mine': True,
            'game_over': True,
            'revealed': game['revealed'],
            'mine_positions': game['mine_positions'],
            'multiplier': 0,
            'winnings': 0,
            'new_balance': float(user.balance)
        })
    
    # Safe tile
    game['revealed'].append(position)
    
    # Calculate current multiplier
    multiplier = calculate_multiplier(len(game['revealed']), 25, game['num_mines'])
    potential_win = game['amount'] * multiplier
    
    # Get user balance
    user = User.query.get(user_id)
    
    return jsonify({
        'success': True,
        'is_mine': False,
        'game_over': False,
        'revealed': game['revealed'],
        'multiplier': multiplier,
        'potential_win': potential_win,
        'tiles_revealed': len(game['revealed']),
        'new_balance': float(user.balance)
    })

@mines_bp.route('/cashout', methods=['POST'])
@jwt_required()
def cashout():
    """Cash out from current game"""
    user_id = get_jwt_identity()
    data = request.json
    
    game_id = data.get('game_id')
    
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = active_games[game_id]
    
    if game['user_id'] != user_id:
        return jsonify({'error': 'Not your game'}), 403
    
    if game['status'] != 'active':
        return jsonify({'error': 'Game is not active'}), 400
    
    if len(game['revealed']) == 0:
        return jsonify({'error': 'Reveal at least one tile before cashing out'}), 400
    
    # Calculate winnings
    multiplier = calculate_multiplier(len(game['revealed']), 25, game['num_mines'])
    winnings = Decimal(str(game['amount'])) * Decimal(str(multiplier))
    profit = winnings - Decimal(str(game['amount']))
    
    # Update balance
    user = User.query.get(user_id)
    user.balance += float(winnings)
    db.session.commit()
    
    # Mark game as complete
    game['status'] = 'won'
    
    return jsonify({
        'success': True,
        'multiplier': multiplier,
        'winnings': float(winnings),
        'profit': float(profit),
        'new_balance': float(user.balance),
        'tiles_revealed': len(game['revealed']),
        'mine_positions': game['mine_positions']
    })

@mines_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's mines history"""
    user_id = get_jwt_identity()
    
    bets = Bet.query.filter_by(
        user_id=user_id,
        bet_type='mines'
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
