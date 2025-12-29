from flask import Blueprint, request, jsonify
from app.models import db, Bet, BetStatus, Match
from app.services.betting_service import BettingService
from app.utils.decorators import token_required
import logging

logger = logging.getLogger(__name__)
bet_bp = Blueprint('betting', __name__, url_prefix='/api/bets')
betting_service = BettingService()


@bet_bp.route('', methods=['POST'])
@token_required
def create_bet(user):
	"""Create a new bet"""
	try:
		# Check if user account is active
		if not user.is_active:
			return jsonify({'message': 'Your account has been suspended. Please contact support.'}), 403
		
		data = request.get_json()

		required_fields = ['amount', 'odds', 'bet_type', 'event_description']
		if not data or not all(field in data for field in required_fields):
			return jsonify({'message': 'Missing required fields'}), 400

		# Try to find and link the match by parsing the event description
		match_id = data.get('match_id')
		if not match_id:
			from app.models import Match
			desc = data['event_description']
			# Try to extract match name (e.g., "Arsenal vs Chelsea - [Match Result] HOME @ 2.00" or "PSG vs Medellin [Correct Score] 3-2 @13.00")
			match_name = None
			if ' vs ' in desc:
				# Try format with " - [" first
				if ' - [' in desc:
					match_name = desc.split(' - [')[0].strip()
				# Try format with " [" (no dash)
				elif ' [' in desc:
					match_name = desc.split(' [')[0].strip()
				
				if match_name:
					teams = match_name.split(' vs ')
					if len(teams) == 2:
						home_team, away_team = teams[0].strip(), teams[1].strip()
						# Find match in database - don't filter by status for settled bets
						match = Match.query.filter(
							Match.home_team == home_team,
							Match.away_team == away_team
						).first()
						if match:
							match_id = match.id
							logger.info(f"Linked bet to match {match_id}: {match_name}")
						else:
							logger.warning(f"Could not find match for: {home_team} vs {away_team}")
		else:
			logger.info(f"Bet created with match_id={match_id} provided from frontend")

		bet = betting_service.create_bet(
			user=user,
			amount=float(data['amount']),
			odds=float(data['odds']),
			bet_type=data['bet_type'],
			event_description=data['event_description'],
			market_type=data.get('market_type'),
			selection=data.get('selection'),
			booking_code=data.get('booking_code'),
			match_id=match_id
		)

		return jsonify({
			'message': 'Bet created successfully',
			'bet': {
				'id': bet.id,
				'amount': bet.amount,
				'odds': bet.odds,
				'potential_payout': bet.potential_payout,
				'bet_type': bet.bet_type,
				'market_type': bet.market_type,
				'selection': bet.selection,
				'status': bet.status,
				'booking_code': bet.booking_code,
				'created_at': bet.created_at.isoformat()
			}
		}), 201

	except ValueError as e:
		return jsonify({'message': str(e)}), 400
	except Exception as e:
		logger.error(f"Bet creation error: {e}")
		return jsonify({'message': 'An error occurred creating bet'}), 500


@bet_bp.route('/<int:bet_id>', methods=['GET'])
@token_required
def get_bet(user, bet_id):
	"""Get bet details"""
	try:
		bet = Bet.query.filter_by(id=bet_id, user_id=user.id).first()

		if not bet:
			return jsonify({'message': 'Bet not found'}), 404

		return jsonify({
			'bet': {
				'id': bet.id,
				'amount': bet.amount,
				'odds': bet.odds,
				'potential_payout': bet.potential_payout,
				'bet_type': bet.bet_type,
				'event_description': bet.event_description,
				'status': bet.status,
				'result': bet.result,
				'settled_payout': bet.settled_payout,
				'created_at': bet.created_at.isoformat(),
				'settled_at': bet.settled_at.isoformat() if bet.settled_at else None
			}
		}), 200
	except Exception as e:
		logger.error(f"Bet fetch error: {e}")
		return jsonify({'message': 'Error fetching bet'}), 500


@bet_bp.route('/user/all', methods=['GET'])
@token_required
def get_user_bets(user):
	"""Get all bets for a user"""
	try:
		status = request.args.get('status')
		
		# Handle "settled" status as won, lost, and cashed out bets
		if status == 'settled':
			bets = betting_service.get_user_bets(user, status=None)
			# Filter to won, lost, and cashed out bets
			bets = [bet for bet in bets if bet.status in ['won', 'lost'] or bet.is_cashed_out]
		else:
			bets = betting_service.get_user_bets(user, status=status)

		bet_list = []
		for bet in bets:
			match_data = None
			if hasattr(betting_service, 'get_bet_match_scores'):
				match_data = betting_service.get_bet_match_scores(bet)
				logger.info(f"Bet {bet.id}: has match_id={bet.match_id}, match_data={match_data}")
			else:
				match_data = {
					'home_team': bet.match.home_team,
					'away_team': bet.match.away_team,
					'home_score': bet.match.home_score,
					'away_score': bet.match.away_score,
					'status': bet.match.status
				} if getattr(bet, 'match', None) else None
			
			bet_list.append({
				'id': bet.id,
				'amount': bet.amount,
				'odds': bet.odds,
				'potential_payout': bet.potential_payout,
				'event_description': getattr(bet, 'event_description', None),
				'bet_type': getattr(bet, 'bet_type', None),
				'market_type': getattr(bet, 'market_type', None),
				'selection': getattr(bet, 'selection', None),
				'status': bet.status,
				'result': getattr(bet, 'result', None),
				'settled_payout': getattr(bet, 'settled_payout', None),
				'booking_code': getattr(bet, 'booking_code', None),
				'is_cashed_out': getattr(bet, 'is_cashed_out', False),
				'cashout_value': getattr(bet, 'cashout_value', None),
				'created_at': bet.created_at.isoformat() if getattr(bet, 'created_at', None) else None,
				'settled_at': bet.settled_at.isoformat() if getattr(bet, 'settled_at', None) else None,
				'match': match_data
			})

		return jsonify({'bets': bet_list}), 200
	except Exception as e:
		logger.error(f"Get user bets error: {e}")
		return jsonify({'message': 'Error fetching bets'}), 500


@bet_bp.route('/active', methods=['GET'])
@token_required
def get_active_bets(user):
	"""Get active bets for a user"""
	try:
		bets = betting_service.get_active_bets(user)

		return jsonify({
			'active_bets': [{
				'id': bet.id,
				'amount': bet.amount,
				'odds': bet.odds,
				'potential_payout': bet.potential_payout,
				'bet_type': getattr(bet, 'bet_type', None),
				'market_type': getattr(bet, 'market_type', None),
				'selection': getattr(bet, 'selection', None),
				'event_description': getattr(bet, 'event_description', None),
				'booking_code': getattr(bet, 'booking_code', None),
				'status': bet.status,
				'is_cashed_out': getattr(bet, 'is_cashed_out', False),
				'cashout_value': getattr(bet, 'cashout_value', None),
				'created_at': bet.created_at.isoformat() if getattr(bet, 'created_at', None) else None,
				'match': bet.match.to_dict() if getattr(bet, 'match', None) else None
			} for bet in bets]
		}), 200
	except Exception as e:
		logger.error(f"Active bets error: {e}")
		return jsonify({'message': 'Error fetching active bets'}), 500


@bet_bp.route('/statistics', methods=['GET'])
@token_required
def get_statistics(user):
	"""Get user betting statistics"""
	try:
		stats = betting_service.get_user_statistics(user)
		return jsonify({'statistics': stats}), 200
	except Exception as e:
		logger.error(f"Statistics error: {e}")
		return jsonify({'message': 'Error fetching statistics'}), 500


@bet_bp.route('/<int:bet_id>/cancel', methods=['POST'])
@token_required
def cancel_bet(user, bet_id):
	"""Cancel a bet"""
	try:
		bet = Bet.query.filter_by(id=bet_id, user_id=user.id).first()

		if not bet:
			return jsonify({'message': 'Bet not found'}), 404

		success = betting_service.cancel_bet(bet, refund=True)

		if success:
			return jsonify({
				'message': 'Bet cancelled successfully',
				'balance': user.balance
			}), 200
		else:
			return jsonify({'message': 'Failed to cancel bet'}), 400

	except Exception as e:
		logger.error(f"Cancel bet error: {e}")
		return jsonify({'message': 'An error occurred'}), 500


@bet_bp.route('/<int:bet_id>/cashout', methods=['POST'])
@token_required
def cashout_bet(user, bet_id):
	"""Cashout an active bet"""
	try:
		bet = Bet.query.filter_by(id=bet_id, user_id=user.id).first()

		if not bet:
			return jsonify({'message': 'Bet not found'}), 404

		if bet.status != BetStatus.ACTIVE.value:
			return jsonify({'message': 'Only active bets can be cashed out'}), 400

		if bet.is_cashed_out:
			return jsonify({'message': 'Bet already cashed out'}), 400

		# Calculate cashout value based on stake amount
		# Before 1 minute: 100% of stake
		# After 1 minute: 85% of stake (15% deduction)
		from datetime import datetime
		time_elapsed = datetime.utcnow() - bet.created_at
		minutes_elapsed = time_elapsed.total_seconds() / 60.0
		
		stake_amount = bet.amount
		
		if minutes_elapsed < 1.0:
			# Before 1 minute: Full stake refund
			cashout_percentage = 1.0
			cashout_value = stake_amount
		else:
			# After 1 minute: 85% of stake (15% deduction)
			cashout_percentage = 0.85
			cashout_value = stake_amount * 0.85

		# Update bet
		bet.is_cashed_out = True
		bet.cashed_out_at = datetime.utcnow()
		bet.cashout_value = cashout_value
		bet.status = BetStatus.CANCELLED.value
		bet.result = 'cashout'
		bet.settled_payout = cashout_value

		# Credit user
		user.balance += cashout_value

		db.session.commit()

		logger.info(f"Bet {bet_id} cashed out: {cashout_value} BTC for user {user.username}")

		return jsonify({
			'message': 'Bet cashed out successfully',
			'cashout_value': cashout_value,
			'balance': user.balance
		}), 200

	except Exception as e:
		logger.error(f"Cashout bet error: {e}")
		db.session.rollback()
		return jsonify({'message': 'An error occurred'}), 500


@bet_bp.route('/<int:bet_id>/cashout-value', methods=['GET'])
@token_required
def get_cashout_value(user, bet_id):
	"""Get current cashout value for a bet"""
	try:
		bet = Bet.query.filter_by(id=bet_id, user_id=user.id).first()

		if not bet:
			return jsonify({'message': 'Bet not found'}), 404

		if bet.status != BetStatus.ACTIVE.value or bet.is_cashed_out:
			return jsonify({'message': 'Cashout not available'}), 400

		# Calculate current cashout value based on stake amount
		# Before 1 minute: 100% of stake
		# After 1 minute: 85% of stake (15% deduction)
		from datetime import datetime
		time_elapsed = datetime.utcnow() - bet.created_at
		minutes_elapsed = time_elapsed.total_seconds() / 60.0
		
		stake_amount = bet.amount
		
		if minutes_elapsed < 1.0:
			# Before 1 minute: Full stake refund
			cashout_percentage = 1.0
			cashout_value = stake_amount
		else:
			# After 1 minute: 85% of stake (15% deduction)
			cashout_percentage = 0.85
			cashout_value = stake_amount * 0.85

		return jsonify({
			'cashout_value': cashout_value,
			'cashout_percentage': cashout_percentage * 100
		}), 200

	except Exception as e:
		logger.error(f"Get cashout value error: {e}")
		return jsonify({'message': 'An error occurred'}), 500


@bet_bp.route('/matches/manual', methods=['GET'])
def get_manual_matches():
	"""Get all matches (both manual and API) - PUBLIC endpoint (no auth required)"""
	try:
		from datetime import datetime, timedelta
		
		# Get today's date (start of day)
		today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
		
		# Get all scheduled and live matches from TODAY onwards (both manual and API)
		matches = Match.query.filter(
			Match.status.in_(['scheduled', 'live']),
			Match.match_date >= today  # Only show today and future matches
		).order_by(Match.match_date.asc()).limit(100).all()
		
		return jsonify({
			'matches': [match.to_dict() for match in matches]
		}), 200
	except Exception as e:
		logger.error(f"Get manual matches error: {e}")
		return jsonify({'message': 'Error fetching matches'}), 500


@bet_bp.route('/test/db-matches', methods=['GET'])
def test_db_matches():
	"""Test endpoint to check database directly - PUBLIC"""
	try:
		all_matches = Match.query.filter_by(is_manual=True).all()
		
		return jsonify({
			'total': len(all_matches),
			'matches': [match.to_dict() for match in all_matches],
			'status': 'success'
		}), 200
	except Exception as e:
		logger.error(f"Database test error: {e}")
		return jsonify({'message': str(e), 'status': 'error'}), 500
