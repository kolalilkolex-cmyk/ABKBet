from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User
from app.models.premium_booking import PremiumBooking, PremiumBookingPurchase
from app.models import Match
from datetime import datetime, timedelta
from sqlalchemy import and_
import logging

logger = logging.getLogger(__name__)
premium_bp = Blueprint('premium', __name__, url_prefix='/api/premium')

@premium_bp.route('/admin/create-booking', methods=['POST'])
@jwt_required()
def create_premium_booking():
    """Admin creates a premium booking code"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        selections = data.get('selections', [])  # [{match_id, market, selection, odds}]
        description = data.get('description', '')
        price_usd = float(data.get('price_usd', 250.0))
        expires_hours = data.get('expires_hours')  # Optional expiration in hours
        
        if not selections or len(selections) == 0:
            return jsonify({'error': 'At least one selection is required'}), 400
        
        # Calculate total odds
        total_odds = 1.0
        for sel in selections:
            total_odds *= float(sel.get('odds', 1.0))
        
        # Generate unique booking code
        booking_code = PremiumBooking.generate_code()
        
        # Create expiration date if specified
        expires_at = None
        if expires_hours:
            expires_at = datetime.utcnow() + timedelta(hours=int(expires_hours))
        
        # Create premium booking
        booking = PremiumBooking(
            booking_code=booking_code,
            selections=selections,
            total_odds=round(total_odds, 2),
            price_usd=price_usd,
            created_by_admin_id=current_user_id,
            description=description,
            expires_at=expires_at
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Premium booking created successfully',
            'booking': booking.to_dict(include_selections=True)
        }), 201
    except Exception as e:
        logger.error(f"Error creating premium booking: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@premium_bp.route('/check-code/<code>', methods=['GET'])
@jwt_required()
def check_premium_code(code):
    """Check if a premium booking code exists and user access"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    booking = PremiumBooking.query.filter_by(booking_code=code.upper()).first()
    
    if not booking:
        return jsonify({'error': 'Invalid booking code'}), 404
    
    # Check if expired
    if booking.expires_at and booking.expires_at < datetime.utcnow():
        return jsonify({'error': 'This booking code has expired'}), 410
    
    if booking.status != 'active':
        return jsonify({'error': f'This booking code is {booking.status}'}), 400
    
    # Convert user balance to USD (1 BTC = $45,000)
    BTC_PRICE_USD = 45000.0
    user_balance_usd = user.balance * BTC_PRICE_USD
    
    # NEW LOGIC: Balance-based access without purchase requirement
    # Users with balance >= $250 can see selections and stake games directly
    # Users with balance < $250 need to deposit to unlock selections
    if user_balance_usd >= 250.0:
        # User has enough balance - show selections immediately
        has_access = True
        requires_deposit = False
        show_selections = True
        deposit_needed = 0.0
    else:
        # User balance < $250 - hide selections until deposit
        has_access = False
        requires_deposit = True
        show_selections = False
        deposit_needed = 250.0 - user_balance_usd
    
    return jsonify({
        'booking': booking.to_dict(include_selections=show_selections),
        'has_access': has_access,
        'requires_deposit': requires_deposit,
        'user_balance_usd': round(user_balance_usd, 2),
        'minimum_balance_required': 250.0,
        'deposit_needed': max(0, 250.0 - user_balance_usd) if user_balance_usd < 250.0 else 0
    }), 200


@premium_bp.route('/purchase/<code>', methods=['POST'])
@jwt_required()
def purchase_premium_booking(code):
    """Legacy endpoint - now access is balance-based, no purchase needed
    Kept for backwards compatibility - just checks balance and grants access"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = PremiumBooking.query.filter_by(booking_code=code.upper()).first()
        
        if not booking:
            return jsonify({'error': 'Invalid booking code'}), 404
        
        # Check if expired
        if booking.expires_at and booking.expires_at < datetime.utcnow():
            return jsonify({'error': 'This booking code has expired'}), 410
        
        if booking.status != 'active':
            return jsonify({'error': f'This booking code is {booking.status}'}), 400
        
        # Use a fixed BTC price for conversions
        BTC_PRICE_USD = 45000.0
        
        # Convert user's BTC balance to USD
        user_balance_usd = user.balance * BTC_PRICE_USD
        
        # NEW LOGIC: Only check balance requirement - no payment needed
        # Users with $250+ can access premium selections and stake games
        if user_balance_usd >= 250.0:
            return jsonify({
                'message': 'Access granted - you can now view and stake this premium booking',
                'booking': booking.to_dict(include_selections=True),
                'has_access': True,
                'user_balance_usd': round(user_balance_usd, 2),
                'note': 'No payment required - access is based on your balance'
            }), 200
        else:
            # User needs to deposit to reach $250 minimum
            deposit_needed = 250.0 - user_balance_usd
            return jsonify({
                'error': 'Insufficient balance to access premium bookings',
                'message': 'Please deposit funds to reach the minimum balance requirement',
                'required_minimum_balance': 250.0,
                'your_balance_usd': round(user_balance_usd, 2),
                'deposit_needed': round(deposit_needed, 2),
                'has_access': False
            }), 403
    except Exception as e:
        logger.error(f"Error checking premium booking access: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@premium_bp.route('/admin/bookings', methods=['GET'])
@jwt_required()
def get_admin_bookings():
    """Get all premium bookings (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    bookings = PremiumBooking.query.order_by(PremiumBooking.created_at.desc()).all()
    
    bookings_data = []
    for booking in bookings:
        booking_dict = booking.to_dict(include_selections=True)
        booking_dict['purchases_count'] = len(booking.purchases)
        booking_dict['revenue'] = len(booking.purchases) * booking.price_usd
        bookings_data.append(booking_dict)
    
    return jsonify({'bookings': bookings_data}), 200


@premium_bp.route('/admin/booking/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_premium_booking(booking_id):
    """Cancel/delete a premium booking (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    booking = PremiumBooking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    booking.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Premium booking cancelled'}), 200


@premium_bp.route('/my-purchases', methods=['GET'])
@jwt_required()
def get_my_purchases():
    """Get user's purchased premium bookings"""
    current_user_id = get_jwt_identity()
    
    purchases = PremiumBookingPurchase.query.filter_by(user_id=current_user_id).order_by(
        PremiumBookingPurchase.purchased_at.desc()
    ).all()
    
    purchases_data = []
    for purchase in purchases:
        booking_data = purchase.booking.to_dict(include_selections=True)
        booking_data['purchased_at'] = purchase.purchased_at.isoformat()
        booking_data['amount_paid_usd'] = purchase.amount_paid_usd
        purchases_data.append(booking_data)
    
    return jsonify({'purchases': purchases_data}), 200


@premium_bp.route('/place-bet/<code>', methods=['POST'])
@jwt_required()
def place_bet_from_premium(code):
    """Place a bet using premium booking selections"""
    try:
        from app.models import Bet
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = PremiumBooking.query.filter_by(booking_code=code.upper()).first()
        
        if not booking:
            return jsonify({'error': 'Invalid booking code'}), 404
        
        # Verify user has purchased this booking
        purchase = PremiumBookingPurchase.query.filter_by(
            booking_id=booking.id,
            user_id=current_user_id
        ).first()
        
        if not purchase:
            return jsonify({'error': 'You must purchase this booking first'}), 403
        
        # Get bet amount from request
        data = request.get_json()
        stake_usd = float(data.get('stake_usd', 0))
        
        if stake_usd <= 0:
            return jsonify({'error': 'Invalid stake amount'}), 400
        
        # Minimum bet check
        if stake_usd < 1.0:
            return jsonify({'error': 'Minimum bet is $1.00'}), 400
        
        # Use fixed BTC price for conversion
        BTC_PRICE_USD = 45000.0
        stake_btc = stake_usd / BTC_PRICE_USD
        
        # Check if user has sufficient balance
        if user.balance < stake_btc:
            return jsonify({
                'error': 'Insufficient balance',
                'required_btc': stake_btc,
                'current_balance': user.balance
            }), 400
        
        # Create event description from selections
        event_description = f"Premium Booking: {booking.booking_code}"
        if booking.selections:
            # Add match details to description
            matches = [sel.get('match', '') for sel in booking.selections[:2]]
            if matches:
                event_description = ' | '.join(matches)
                if len(booking.selections) > 2:
                    event_description += f" (+{len(booking.selections) - 2} more)"
        
        # Calculate potential payout
        potential_payout_btc = stake_btc * booking.total_odds
        
        # Create the bet
        bet = Bet(
            user_id=current_user_id,
            event_description=event_description,
            amount=stake_btc,
            odds=booking.total_odds,
            potential_payout=potential_payout_btc,
            status='pending',
            booking_code=booking.booking_code
        )
        
        # Deduct stake from user balance
        user.balance -= stake_btc
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify({
            'message': 'Bet placed successfully! 🎉',
            'bet': {
                'id': bet.id,
                'event_description': bet.event_description,
                'stake_usd': stake_usd,
                'stake_btc': stake_btc,
                'odds': bet.odds,
                'potential_payout_usd': stake_usd * bet.odds,
                'potential_payout_btc': potential_payout_btc,
                'booking_code': booking.booking_code,
                'status': bet.status,
                'created_at': bet.created_at.isoformat()
            },
            'new_balance_btc': user.balance,
            'new_balance_usd': user.balance * BTC_PRICE_USD
        }), 201
        
    except Exception as e:
        logger.error(f"Error placing bet from premium booking: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
