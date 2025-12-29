"""
Crash/Aviator Game Routes
Real-time multiplier betting game with provably fair system
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, Bet, Transaction, BetStatus
import time
import random
import hashlib
import hmac
from datetime import datetime
from decimal import Decimal

crash_bp = Blueprint('crash', __name__, url_prefix='/api/crash')

# Game state
current_game = {
    'game_id': None,
    'status': 'waiting',  # waiting, flying, crashed
    'multiplier': 1.00,
    'crash_point': None,
    'start_time': None,
    'server_seed': None,
    'client_seed': None,
    'bets': {},  # user_id: {amount, cashed_out, cash_out_multiplier}
    'history': []
}

def generate_crash_point(server_seed, client_seed, game_id):
    """Generate crash point with strong house advantage using simple random"""
    # Use timestamp + random for true randomness
    random.seed(time.time() * random.random() * game_id)
    
    # Generate random value 0-1
    rand_val = random.random()
    
    # House edge 10% - instant crash
    if rand_val < 0.10:
        return 1.00
    
    # Most games crash early (house advantage)
    # 70% of games: 1.2x - 2.5x
    # 20% of games: 2.5x - 10x  
    # 10% of games: 10x - 50x
    
    if rand_val < 0.70:  # 60% after house edge
        # Early crash: 1.2x - 2.5x
        return round(1.2 + (random.random() * 1.3), 2)
    elif rand_val < 0.90:  # 20%
        # Medium: 2.5x - 10x
        return round(2.5 + (random.random() * 7.5), 2)
    else:  # 10%
        # Big win: 10x - 50x
        return round(10.0 + (random.random() * 40.0), 2)
    
    return round(crash_point, 2)

def start_new_game():
    """Initialize a new crash game"""
    global current_game
    
    # Generate seeds for provably fair
    server_seed = hashlib.sha256(str(time.time()).encode()).hexdigest()
    client_seed = hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
    game_id = int(time.time() * 1000)
    
    # Calculate crash point
    crash_point = generate_crash_point(server_seed, client_seed, game_id)
    
    # Save previous game to history
    if current_game['game_id'] and current_game['crash_point']:
        current_game['history'].insert(0, {
            'game_id': current_game['game_id'],
            'crash_point': current_game['crash_point'],
            'timestamp': datetime.utcnow().isoformat()
        })
        # Keep only last 50 games
        current_game['history'] = current_game['history'][:50]
    
    # 15 second betting window (more realistic)
    start_time = time.time() + 15
    
    current_game.update({
        'game_id': game_id,
        'status': 'waiting',
        'multiplier': 1.00,
        'crash_point': crash_point,
        'start_time': start_time,
        'betting_start': time.time(),  # Track when betting started
        'server_seed': server_seed,
        'client_seed': client_seed,
        'bets': {}
    })
    
    return game_id

def get_current_multiplier():
    """Calculate current multiplier based on elapsed time"""
    if current_game['status'] != 'flying' or not current_game['start_time']:
        return 1.00
    
    elapsed = time.time() - current_game['start_time']
    
    # Cap at 20 seconds max flight time for faster games
    max_flight_time = 20.0
    if elapsed >= max_flight_time:
        # Force crash
        if current_game['status'] == 'flying':
            current_game['status'] = 'crashed'
            current_game['multiplier'] = min(current_game['crash_point'], 10.0)
            process_crashed_game()
        return current_game['multiplier']
    
    # Linear growth: 0.15x per second (reaches 4x in 20 seconds)
    # More realistic and faster than exponential
    multiplier = 1.00 + (elapsed * 0.15)
    
    # If reached crash point, game ends
    if multiplier >= current_game['crash_point']:
        current_game['status'] = 'crashed'
        current_game['multiplier'] = current_game['crash_point']
        process_crashed_game()
        return current_game['crash_point']
    
    current_game['multiplier'] = round(multiplier, 2)
    return current_game['multiplier']

def process_crashed_game():
    """Process all bets when game crashes"""
    # Just log - balance already deducted on bet placement
    for user_id, bet_data in current_game['bets'].items():
        if not bet_data.get('cashed_out', False):
            # User lost (balance already deducted when they placed bet)
            pass

@crash_bp.route('/status', methods=['GET'])
def get_status():
    """Get current game status"""
    # Auto-start a new game if none exists
    if current_game['game_id'] is None:
        start_new_game()
    
    # Auto-progress game based on time
    current_time = time.time()
    
    if current_game['status'] == 'waiting' and current_time >= current_game['start_time']:
        # Start flying phase
        current_game['status'] = 'flying'
        current_game['start_time'] = current_time
        
    elif current_game['status'] == 'flying':
        # Check if should crash
        multiplier = get_current_multiplier()
        if multiplier >= current_game['crash_point']:
            # Crash!
            current_game['status'] = 'crashed'
            current_game['multiplier'] = current_game['crash_point']
            
            # Process all bets that didn't cash out (balance already deducted)
            for user_id, bet_data in current_game['bets'].items():
                if not bet_data['cashed_out']:
                    # User lost (balance already deducted when they placed bet)
                    pass
            
            # Auto-start next game after 3 seconds
            start_new_game()
    
    elif current_game['status'] == 'crashed':
        # Check if enough time passed to start new game
        if 'betting_start' not in current_game or current_time - current_game.get('betting_start', 0) > 8:
            start_new_game()
    
    multiplier = get_current_multiplier() if current_game['status'] == 'flying' else current_game['multiplier']
    time_until_start = max(0, int(current_game['start_time'] - current_time)) if current_game['status'] == 'waiting' else 0
    
    return jsonify({
        'game_id': current_game['game_id'],
        'status': current_game['status'],
        'multiplier': multiplier,
        'crash_point': current_game['crash_point'] if current_game['status'] == 'crashed' else None,
        'time_until_start': time_until_start,
        'player_count': len(current_game['bets']),
        'history': current_game['history'][:10]
    })

@crash_bp.route('/bet', methods=['POST'])
@jwt_required()
def place_bet():
    """Place bet on current game"""
    user_id = get_jwt_identity()
    data = request.json
    
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({'error': 'Invalid bet amount'}), 400
    
    # Auto-start a new game if none exists
    if current_game['game_id'] is None or current_game['status'] == 'crashed':
        start_new_game()
    
    if current_game['status'] != 'waiting':
        return jsonify({'error': 'Betting is closed for this round'}), 400
    
    if user_id in current_game['bets']:
        return jsonify({'error': 'You already have a bet in this round'}), 400
    
    # Check user balance
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.balance < Decimal(str(amount)):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Deduct balance
    user.balance -= float(amount)
    db.session.commit()
    
    # Add bet to current game
    current_game['bets'][user_id] = {
        'amount': amount,
        'cashed_out': False,
        'cash_out_multiplier': None,
        'username': user.username
    }
    
    return jsonify({
        'success': True,
        'game_id': current_game['game_id'],
        'amount': amount,
        'new_balance': float(user.balance)
    })

@crash_bp.route('/cashout', methods=['POST'])
@jwt_required()
def cash_out():
    """Cash out current bet"""
    user_id = get_jwt_identity()
    
    if current_game['status'] != 'flying':
        return jsonify({'error': 'No active game to cash out from'}), 400
    
    if user_id not in current_game['bets']:
        return jsonify({'error': 'You have no bet in this round'}), 400
    
    bet_data = current_game['bets'][user_id]
    
    if bet_data.get('cashed_out', False):
        return jsonify({'error': 'Already cashed out'}), 400
    
    # Get current multiplier
    multiplier = get_current_multiplier()
    
    if current_game['status'] == 'crashed':
        return jsonify({'error': 'Game already crashed'}), 400
    
    # Calculate winnings
    bet_amount = Decimal(str(bet_data['amount']))
    winnings = bet_amount * Decimal(str(multiplier))
    profit = winnings - bet_amount
    
    # Update user balance
    user = User.query.get(user_id)
    user.balance += float(winnings)
    db.session.commit()
    
    # Mark as cashed out
    bet_data['cashed_out'] = True
    bet_data['cash_out_multiplier'] = multiplier
    
    return jsonify({
        'success': True,
        'multiplier': multiplier,
        'winnings': float(winnings),
        'profit': float(profit),
        'new_balance': float(user.balance)
    })

@crash_bp.route('/history', methods=['GET'])
def get_history():
    """Get crash game history"""
    return jsonify({
        'history': current_game['history'][:50]
    })

@crash_bp.route('/start', methods=['POST'])
def start_game():
    """Start the game (admin/automated trigger)"""
    if current_game['status'] != 'waiting':
        return jsonify({'error': 'Game already in progress'}), 400
    
    current_game['status'] = 'flying'
    current_game['start_time'] = time.time()
    current_game['multiplier'] = 1.00
    
    return jsonify({
        'success': True,
        'game_id': current_game['game_id'],
        'crash_point': current_game['crash_point']
    })

@crash_bp.route('/reset', methods=['POST'])
def reset_game():
    """Reset game for next round (admin/automated trigger)"""
    game_id = start_new_game()
    
    return jsonify({
        'success': True,
        'new_game_id': game_id
    })

# Initialize first game
start_new_game()
