from flask import Blueprint, request, jsonify, current_app
from app.models import db, Bet, User, Transaction, BetStatus, Match, MatchStatus
from app.models.deposit import DepositRequest
from app.models.payment_method import PaymentMethod
from app.services.betting_service import BettingService
from app.utils.decorators import token_required
import logging, os, uuid
from datetime import datetime

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
betting_service = BettingService()

# --- Admin check decorator ---
def admin_required(f):
    @token_required
    def wrapper(user, *args, **kwargs):
        if not getattr(user, 'is_admin', False):
            return jsonify({'message': 'Admin access required'}), 403
        return f(user, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# --- Platform Statistics ---
@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_platform_statistics(user):
    try:
        # Basic counts
        total_users = User.query.count()
        active_bets = Bet.query.filter_by(status=BetStatus.ACTIVE.value).count()
        pending_deposits_count = Transaction.query.filter_by(transaction_type='deposit', status='pending').count()
        pending_withdrawals_count = Transaction.query.filter_by(transaction_type='withdrawal', status='pending').count()
        
        # Betting statistics
        betting_volume_btc = db.session.query(db.func.sum(Bet.amount)).scalar() or 0
        total_payouts_btc = db.session.query(db.func.sum(Bet.settled_payout)).scalar() or 0
        
        # Financial statistics (deposits/withdrawals)
        total_deposits_btc = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'deposit',
            Transaction.status == 'completed'
        ).scalar() or 0
        
        total_withdrawals_btc = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == 'withdrawal',
            Transaction.status == 'completed'
        ).scalar() or 0
        
        # Calculate net revenue (deposits - withdrawals - outstanding bets)
        outstanding_bets_btc = db.session.query(db.func.sum(Bet.amount)).filter(
            Bet.status.in_([BetStatus.ACTIVE.value, BetStatus.PENDING.value])
        ).scalar() or 0
        
        net_revenue_btc = total_deposits_btc - total_withdrawals_btc - outstanding_bets_btc

        # Values are already in USD - no conversion needed
        
        return jsonify({
            # Basic counts
            'total_users': total_users,
            'active_bets': active_bets,
            'pending_deposits': pending_deposits_count,
            'pending_withdrawals': pending_withdrawals_count,
            
            # Betting statistics (already in USD)
            'betting_volume': betting_volume_btc,
            'total_payouts': total_payouts_btc,
            
            # Financial statistics (already in USD)
            'total_deposits': total_deposits_btc,
            'total_withdrawals': total_withdrawals_btc,
            'outstanding_bets': outstanding_bets_btc,
            'net_revenue': net_revenue_btc
        }), 200
    except Exception as e:
        logger.error(f"[Platform Stats] Error: {e}")
        return jsonify({'message': 'Error fetching statistics'}), 500

# --- Recent Activity ---
@admin_bp.route('/activity/recent', methods=['GET'])
@admin_required
def get_recent_activity(user):
    """Get combined recent activity from bets, transactions, and users"""
    try:
        limit = request.args.get('limit', 20, type=int)
        activities = []
        
        # Recent Bets
        recent_bets = Bet.query.order_by(Bet.created_at.desc()).limit(limit).all()
        for bet in recent_bets:
            activities.append({
                'time': bet.created_at.isoformat(),
                'type': 'bet_placed',
                'user': bet.user.username,
                'amount': bet.amount,
                'status': bet.status,
                'description': f"Placed bet at {bet.odds}x odds"
            })
        
        # Recent Transactions
        recent_txs = Transaction.query.order_by(Transaction.created_at.desc()).limit(limit).all()
        for tx in recent_txs:
            activities.append({
                'time': tx.created_at.isoformat(),
                'type': tx.transaction_type,
                'user': tx.user.username,
                'amount': tx.amount,
                'status': tx.status,
                'description': f"{tx.transaction_type.title()} transaction"
            })
        
        # Recent Bet Settlements
        recent_settled = Bet.query.filter(Bet.settled_at.isnot(None)).order_by(Bet.settled_at.desc()).limit(limit).all()
        for bet in recent_settled:
            activities.append({
                'time': bet.settled_at.isoformat(),
                'type': 'bet_settled',
                'user': bet.user.username,
                'amount': bet.settled_payout if bet.settled_payout else 0,
                'status': bet.result,
                'description': f"Bet {bet.result}: {bet.settled_payout or 0:.8f} BTC"
            })
        
        # Recent User Registrations
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        for u in recent_users:
            activities.append({
                'time': u.created_at.isoformat(),
                'type': 'user_registered',
                'user': u.username,
                'amount': 0,
                'status': 'active' if u.is_active else 'inactive',
                'description': 'New user registration'
            })
        
        # Sort by time descending and limit
        activities.sort(key=lambda x: x['time'], reverse=True)
        activities = activities[:limit]
        
        return jsonify({'activities': activities}), 200
    except Exception as e:
        logger.error(f"[Recent Activity] Error: {e}")
        return jsonify({'message': 'Error fetching recent activity'}), 500

# --- Pending Deposits ---
@admin_bp.route('/deposits/pending', methods=['GET'])
@admin_required
def get_pending_deposits(user):
    try:
        deposits = Transaction.query.filter_by(
            transaction_type='deposit',
            status='pending'
        ).order_by(Transaction.created_at.desc()).all()

        return jsonify({
            'deposits': [{
                'id': tx.id,
                'user_id': tx.user_id,
                'username': tx.user.username,
                'amount': tx.amount,
                'payment_method': tx.payment_method,
                'tx_hash': tx.tx_hash,
                'created_at': tx.created_at.isoformat()
            } for tx in deposits]
        }), 200
    except Exception as e:
        logger.error(f"[Pending Deposits] Error: {e}")
        return jsonify({'message': 'Error fetching pending deposits'}), 500

# --- Approve Deposit ---
@admin_bp.route('/deposits/<int:tx_id>/approve', methods=['POST'])
@admin_required
def approve_deposit(user, tx_id):
    try:
        transaction = db.session.get(Transaction, tx_id)
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), 404

        if transaction.status != 'pending':
            return jsonify({'message': 'Transaction is not pending'}), 400

        # Update transaction
        transaction.status = 'completed'
        
        # Credit user balance
        target_user = db.session.get(User, transaction.user_id)
        if target_user:
            target_user.balance += transaction.amount

        db.session.commit()

        logger.info(f"Admin {user.username} approved deposit {tx_id} for user {target_user.username}")

        return jsonify({
            'message': 'Deposit approved successfully',
            'transaction_id': tx_id,
            'user_balance': target_user.balance
        }), 200
    except Exception as e:
        logger.error(f"[Approve Deposit] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error approving deposit'}), 500

# --- Reject Deposit ---
@admin_bp.route('/deposits/<int:tx_id>/reject', methods=['POST'])
@admin_required
def reject_deposit(user, tx_id):
    try:
        transaction = db.session.get(Transaction, tx_id)
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), 404

        if transaction.status != 'pending':
            return jsonify({'message': 'Transaction is not pending'}), 400

        transaction.status = 'failed'
        db.session.commit()

        logger.info(f"Admin {user.username} rejected deposit {tx_id}")

        return jsonify({
            'message': 'Deposit rejected',
            'transaction_id': tx_id
        }), 200
    except Exception as e:
        logger.error(f"[Reject Deposit] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error rejecting deposit'}), 500

# --- Pending Withdrawals ---
@admin_bp.route('/withdrawals/pending', methods=['GET'])
@admin_required
def get_pending_withdrawals(user):
    try:
        withdrawals = Transaction.query.filter_by(
            transaction_type='withdrawal',
            status='pending'
        ).order_by(Transaction.created_at.desc()).all()

        return jsonify({
            'withdrawals': [{
                'id': tx.id,
                'user_id': tx.user_id,
                'username': tx.user.username,
                'amount': tx.amount,
                'to_address': tx.to_address,
                'created_at': tx.created_at.isoformat()
            } for tx in withdrawals]
        }), 200
    except Exception as e:
        logger.error(f"[Pending Withdrawals] Error: {e}")
        return jsonify({'message': 'Error fetching pending withdrawals'}), 500

# --- Process Withdrawal ---
@admin_bp.route('/withdrawals/<int:tx_id>/process', methods=['POST'])
@admin_required
def process_withdrawal(user, tx_id):
    try:
        data = request.get_json()
        blockchain_tx_hash = data.get('tx_hash')  # Actual blockchain transaction hash

        transaction = db.session.get(Transaction, tx_id)
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), 404

        if transaction.status != 'pending':
            return jsonify({'message': 'Transaction is not pending'}), 400

        # Update with actual blockchain hash
        if blockchain_tx_hash:
            transaction.tx_hash = blockchain_tx_hash
        transaction.status = 'completed'
        
        db.session.commit()

        logger.info(f"Admin {user.username} processed withdrawal {tx_id}")

        return jsonify({
            'message': 'Withdrawal processed successfully',
            'transaction_id': tx_id,
            'tx_hash': transaction.tx_hash
        }), 200
    except Exception as e:
        logger.error(f"[Process Withdrawal] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error processing withdrawal'}), 500

# --- Adjust User Balance ---
@admin_bp.route('/users/<int:user_id>/balance', methods=['POST'])
@admin_required
def adjust_user_balance(user, user_id):
    try:
        data = request.get_json()
        amount = data.get('amount')
        reason = data.get('reason', 'Admin adjustment')

        if amount is None:
            return jsonify({'message': 'Amount is required'}), 400

        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404

        old_balance = target_user.balance
        target_user.balance += float(amount)
        
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            amount=abs(float(amount)),
            transaction_type='deposit' if amount > 0 else 'withdrawal',
            status='completed',
            tx_hash=f'ADMIN_ADJ_{uuid.uuid4().hex[:8]}',
            from_address='ADMIN',
            to_address=target_user.username,
            payment_method='admin_adjustment'
        )
        db.session.add(transaction)
        db.session.commit()

        logger.info(f"Admin {user.username} adjusted balance for {target_user.username}: {amount}. Reason: {reason}")

        return jsonify({
            'message': 'Balance adjusted successfully',
            'old_balance': old_balance,
            'new_balance': target_user.balance
        }), 200
    except Exception as e:
        logger.error(f"[Adjust Balance] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error adjusting balance'}), 500

# --- Settle Bet ---
@admin_bp.route('/bets/<int:bet_id>/settle', methods=['POST'])
@admin_required
def settle_bet(user, bet_id):
    try:
        data = request.get_json()
        result = data.get('result')
        payout = data.get('payout')

        if not result:
            return jsonify({'message': 'Missing result field'}), 400

        bet = db.session.get(Bet, bet_id)
        if not bet:
            return jsonify({'message': 'Bet not found'}), 404

        success = betting_service.settle_bet(bet, result, payout)
        if success:
            return jsonify({
                'message': 'Bet settled successfully',
                'bet': {
                    'id': bet.id,
                    'result': bet.result,
                    'settled_payout': bet.settled_payout
                }
            }), 200
        return jsonify({'message': 'Failed to settle bet'}), 400

    except Exception as e:
        logger.error(f"[Settle Bet] Error for bet_id={bet_id}: {e}")
        return jsonify({'message': 'An error occurred'}), 500

# --- List Users ---
@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users(user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        users = User.query.paginate(page=page, per_page=per_page)

        return jsonify({
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'balance': u.balance,
                'is_active': u.is_active,
                'is_admin': u.is_admin,
                'created_at': u.created_at.isoformat()
            } for u in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"[List Users] Error: {e}")
        return jsonify({'message': 'Error fetching users'}), 500

# --- Get User Details ---
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details(user, user_id):
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404

        stats = betting_service.get_user_statistics(target_user)
        return jsonify({
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'email': target_user.email,
                'balance': target_user.balance,
                'created_at': target_user.created_at.isoformat(),
                'statistics': stats
            }
        }), 200
    except Exception as e:
        logger.error(f"[User Details] Error for user_id={user_id}: {e}")
        return jsonify({'message': 'Error fetching user details'}), 500

# --- List Transactions ---
@admin_bp.route('/transactions', methods=['GET'])
@admin_required
def list_transactions(user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')

        query = Transaction.query
        if status:
            query = query.filter_by(status=status)

        transactions = query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page)

        transactions_data = []
        for tx in transactions.items:
            try:
                # Safely get username - handle case where user might be deleted
                username = tx.user.username if tx.user else f"User#{tx.user_id}"
                
                transactions_data.append({
                    'id': tx.id,
                    'user_id': tx.user_id,
                    'username': username,
                    'tx_hash': tx.tx_hash,
                    'amount': tx.amount,
                    'type': tx.transaction_type,
                    'status': tx.status,
                    'created_at': tx.created_at.isoformat()
                })
            except Exception as tx_error:
                # Log the specific transaction that caused an error but continue
                logger.error(f"[List Transactions] Error processing transaction {tx.id}: {tx_error}")
                continue

        return jsonify({
            'transactions': transactions_data,
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"[List Transactions] Error: {e}", exc_info=True)
        return jsonify({'message': f'Error fetching transactions: {str(e)}'}), 500

# --- List All Bets ---
@admin_bp.route('/bets', methods=['GET'])
@admin_required
def list_bets(user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')

        query = Bet.query
        if status:
            query = query.filter_by(status=status)

        bets = query.order_by(Bet.created_at.desc()).paginate(page=page, per_page=per_page)

        bets_data = []
        for bet in bets.items:
            try:
                # Safely get username - handle case where user might be deleted
                username = bet.user.username if bet.user else f"User#{bet.user_id}"
                
                bet_dict = {
                    'id': bet.id,
                    'user_id': bet.user_id,
                    'username': username,
                    'amount': bet.amount,
                    'odds': bet.odds,
                    'potential_payout': bet.potential_payout,
                    'event_description': bet.event_description,
                    'selection': bet.selection,
                    'booking_code': bet.booking_code,
                    'status': bet.status,
                    'result': bet.result,
                    'settled_payout': bet.settled_payout,
                    'created_at': bet.created_at.isoformat(),
                    'settled_at': bet.settled_at.isoformat() if bet.settled_at else None
                }
                
                # Add match details if available
                if bet.match:
                    bet_dict['match'] = {
                        'id': bet.match.id,
                        'home_team': bet.match.home_team,
                        'away_team': bet.match.away_team,
                        'league': bet.match.league,
                        'status': bet.match.status,
                        'home_score': bet.match.home_score,
                        'away_score': bet.match.away_score,
                        'match_time': bet.match.match_time.isoformat() if bet.match.match_time else None
                    }
                
                bets_data.append(bet_dict)
            except Exception as bet_error:
                # Log the specific bet that caused an error but continue processing others
                logger.error(f"[List Bets] Error processing bet {bet.id}: {bet_error}")
                continue

        return jsonify({
            'bets': bets_data,
            'total': bets.total,
            'pages': bets.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"[List Bets] Error: {e}", exc_info=True)
        return jsonify({'message': f'Error fetching bets: {str(e)}'}), 500

# ===== MATCH MANAGEMENT =====

# --- List All Matches (Manual Only) ---
@admin_bp.route('/matches', methods=['GET'])
@admin_required
def list_matches(user):
    """Get all matches (manual and API-based) for admin"""
    try:
        # Check if we should show only manual matches
        show_manual_only = request.args.get('manual_only', 'true').lower() == 'true'
        
        if show_manual_only:
            # Get only manual matches that are not completed or cancelled, earliest first
            matches = Match.query.filter(
                Match.is_manual == True,
                Match.status.notin_(['completed', 'cancelled', 'settled'])
            ).order_by(Match.match_date.asc()).all()
            
            # If no matches with specific status filter, get recent manual matches
            if not matches:
                matches = Match.query.filter(Match.is_manual == True).order_by(Match.match_date.asc()).limit(100).all()
        else:
            # Get all matches that are not completed or cancelled, earliest first
            matches = Match.query.filter(
                Match.status.notin_(['completed', 'cancelled', 'settled'])
            ).order_by(Match.match_date.asc()).all()
            
            # If no matches with specific status filter, get all matches (earliest first)
            if not matches:
                matches = Match.query.order_by(Match.match_date.asc()).limit(100).all()
        
        return jsonify({
            'matches': [match.to_dict() for match in matches]
        }), 200
    except Exception as e:
        logger.error(f"[List Matches] Error: {e}")
        return jsonify({'message': 'Error fetching matches'}), 500

@admin_bp.route('/fetch-matches', methods=['POST'])
@admin_required
def fetch_matches_from_api(user):
    """Fetch matches from ALL sports API and save to database"""
    try:
        from app.services.multi_sport_api_service import multi_sport_api
        from config import Config
        
        # Check if API key is configured
        api_key = os.environ.get('FOOTBALL_API_KEY') or getattr(Config, 'FOOTBALL_API_KEY', None)
        
        if not api_key:
            return jsonify({
                'message': 'API key not configured. Please set FOOTBALL_API_KEY environment variable.'
            }), 400
        
        # Use the global instance and initialize it
        multi_sport_api.initialize(api_key)
        
        # Fetch matches from ALL SPORTS (8 prioritized sports)
        logger.info("="*50)
        logger.info("STARTING MULTI-SPORT API FETCH")
        logger.info(f"API Key configured: {api_key[:10]}...")
        logger.info("="*50)
        
        matches_data = multi_sport_api.get_all_sports_matches(days_ahead=7)
        
        logger.info(f"Total matches fetched from all sports: {len(matches_data) if matches_data else 0}")
        logger.info(f"Total matches fetched from all sports: {len(matches_data) if matches_data else 0}")
        
        if not matches_data:
            logger.warning("No matches returned from any sport!")
            return jsonify({'message': 'No matches available today from any sport. Check logs for details.'}), 404
        
        logger.info(f"Fetched {len(matches_data)} total matches from API")
        
        # Sync to database
        created, updated = multi_sport_api.sync_matches_to_database(matches_data)
        
        logger.info(f"Database sync complete: {created} created, {updated} updated")
        logger.info("="*50)
        
        return jsonify({
            'message': f'Successfully fetched matches from {len(matches_data)} sports!',
            'created': created,
            'updated': updated,
            'total': created + updated
        }), 200
        
    except Exception as e:
        logger.error(f"Fetch matches error: {e}")
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/update-live-matches', methods=['POST'])
@admin_required
def update_live_matches_endpoint(user):
    """Update scores and times for all live matches"""
    try:
        from app.services.multi_sport_api_service import multi_sport_api
        from config import Config
        
        api_key = os.environ.get('FOOTBALL_API_KEY') or getattr(Config, 'FOOTBALL_API_KEY', None)
        
        if not api_key:
            return jsonify({'message': 'API key not configured'}), 400
        
        multi_sport_api.initialize(api_key)
        
        logger.info("="*50)
        logger.info("UPDATING LIVE MATCHES")
        logger.info("="*50)
        
        updated = multi_sport_api.update_live_matches()
        
        logger.info("="*50)
        
        return jsonify({
            'message': f'Successfully updated {updated} live matches',
            'updated': updated
        }), 200
        
    except Exception as e:
        logger.error(f"[Fetch Matches] Error: {e}")
        db.session.rollback()
        return jsonify({'message': f'Error fetching matches: {str(e)}'}), 500

# --- Create New Match ---
@admin_bp.route('/matches', methods=['POST'])
@admin_required
def create_match(user):
    """Create a new manually managed match"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['home_team', 'away_team', 'match_date', 'home_odds', 'draw_odds', 'away_odds']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Parse date
        try:
            match_date = datetime.fromisoformat(data['match_date'].replace('Z', '+00:00'))
        except:
            return jsonify({'message': 'Invalid date format'}), 400
        
        # Create match
        match = Match(
            home_team=data['home_team'],
            away_team=data['away_team'],
            league=data.get('league'),
            match_date=match_date,
            home_odds=float(data['home_odds']),
            draw_odds=float(data['draw_odds']),
            away_odds=float(data['away_odds']),
            # Optional betting markets
            home_draw_odds=float(data['home_draw_odds']) if 'home_draw_odds' in data else None,
            home_away_odds=float(data['home_away_odds']) if 'home_away_odds' in data else None,
            draw_away_odds=float(data['draw_away_odds']) if 'draw_away_odds' in data else None,
            gg_odds=float(data['gg_odds']) if 'gg_odds' in data else None,
            ng_odds=float(data['ng_odds']) if 'ng_odds' in data else None,
            over15_odds=float(data['over15_odds']) if 'over15_odds' in data else None,
            under15_odds=float(data['under15_odds']) if 'under15_odds' in data else None,
            over25_odds=float(data['over25_odds']) if 'over25_odds' in data else None,
            under25_odds=float(data['under25_odds']) if 'under25_odds' in data else None,
            over35_odds=float(data['over35_odds']) if 'over35_odds' in data else None,
            under35_odds=float(data['under35_odds']) if 'under35_odds' in data else None,
            # HT/FT and Correct Score (as JSON strings)
            htft_odds=data.get('htft_odds'),
            correct_score_odds=data.get('correct_score_odds'),
            status=MatchStatus.SCHEDULED.value,
            is_manual=True
        )
        
        db.session.add(match)
        db.session.commit()
        
        logger.info(f"Admin {user.username} created match: {match.home_team} vs {match.away_team}")
        
        return jsonify({
            'message': 'Match created successfully',
            'match': match.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"[Create Match] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error creating match'}), 500

# --- Get Single Match ---
@admin_bp.route('/matches/<int:match_id>', methods=['GET'])
@admin_required
def get_match(user, match_id):
    """Get details of a specific match"""
    try:
        match = db.session.get(Match, match_id)
        if not match:
            return jsonify({'message': 'Match not found'}), 404
        
        return jsonify({'match': match.to_dict()}), 200
    except Exception as e:
        logger.error(f"[Get Match] Error: {e}")
        return jsonify({'message': 'Error fetching match'}), 500

# --- Update Match ---
@admin_bp.route('/matches/<int:match_id>', methods=['PUT'])
@admin_required
def update_match(user, match_id):
    """Update match details (teams, odds, date, etc.)"""
    try:
        match = db.session.get(Match, match_id)
        if not match:
            return jsonify({'message': 'Match not found'}), 404
        
        if not match.is_manual:
            return jsonify({'message': 'Cannot edit API-based matches'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'home_team' in data:
            match.home_team = data['home_team']
        if 'away_team' in data:
            match.away_team = data['away_team']
        if 'league' in data:
            match.league = data['league']
        if 'match_date' in data:
            try:
                match.match_date = datetime.fromisoformat(data['match_date'].replace('Z', '+00:00'))
            except:
                return jsonify({'message': 'Invalid date format'}), 400
        if 'home_odds' in data:
            match.home_odds = float(data['home_odds'])
        if 'draw_odds' in data:
            match.draw_odds = float(data['draw_odds'])
        if 'away_odds' in data:
            match.away_odds = float(data['away_odds'])
        
        db.session.commit()
        
        logger.info(f"Admin {user.username} updated match {match_id}")
        
        return jsonify({
            'message': 'Match updated successfully',
            'match': match.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[Update Match] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error updating match'}), 500

# --- Update Match Result ---
@admin_bp.route('/matches/<int:match_id>/result', methods=['POST'])
@admin_required
def update_match_result(user, match_id):
    """Update match score and status, settle related bets"""
    try:
        match = db.session.get(Match, match_id)
        if not match:
            return jsonify({'message': 'Match not found'}), 404
        
        data = request.get_json()
        
        # Check if this is halftime or fulltime result
        if 'ht_home_score' in data or 'ht_away_score' in data:
            # Update halftime score
            if 'ht_home_score' in data:
                match.ht_home_score = int(data['ht_home_score'])
            if 'ht_away_score' in data:
                match.ht_away_score = int(data['ht_away_score'])
            if 'ht_status' in data:
                match.ht_status = data['ht_status']
            
            db.session.commit()
            logger.info(f"Admin {user.username} updated half-time result for match {match_id}")
            
            return jsonify({
                'message': 'Half-time result updated successfully',
                'match': match.to_dict()
            }), 200
        
        # Update fulltime score and status
        if 'home_score' in data:
            match.home_score = int(data['home_score'])
        if 'away_score' in data:
            match.away_score = int(data['away_score'])
        if 'status' in data:
            match.status = data['status']
        
        # If match is finished, settle all bets
        if match.status == MatchStatus.FINISHED.value and match.home_score is not None and match.away_score is not None:
            # Settle all bets on this match (both by match_id and by description matching)
            match_name = f"{match.home_team} vs {match.away_team}"
            match_name_alt = f"{match.home_team} vs. {match.away_team}"
            
            # Find bets by match_id or by matching the match name in description
            bets = Bet.query.filter(
                Bet.status == BetStatus.ACTIVE.value,
                db.or_(
                    Bet.match_id == match_id,
                    Bet.event_description.like(f'%{match_name}%'),
                    Bet.event_description.like(f'%{match_name_alt}%')
                )
            ).all()
            
            settled_count = 0
            for bet in bets:
                is_won = False
                bet_matched = False  # Track if we could determine the bet type
                
                # Parse the bet to determine if it won
                desc = bet.event_description
                desc_lower = desc.lower()
                market = bet.market_type or ''
                selection = bet.selection or ''
                
                logger.info(f"\n{'='*60}")
                logger.info(f"Settling bet {bet.id}")
                logger.info(f"  Market: {market}")
                logger.info(f"  Selection (raw): '{selection}'")
                logger.info(f"  Description: {desc}")
                logger.info(f"  Match: {match.home_team} {match.home_score}-{match.away_score} {match.away_team}")
                
                # Extract selection from description (e.g., "[Match Result] HOME @2.00")
                selection_match = None
                if '[Match Result]' in desc or 'match result' in desc_lower or '1x2' in market.lower():
                    bet_matched = True
                    # Try to extract from selection field first
                    if selection:
                        selection_match = selection.strip().lower()
                        logger.info(f"  Using selection field: '{selection_match}'")
                    # Otherwise parse from description - look for HOME, AWAY, DRAW (case insensitive)
                    else:
                        # Extract the part after ] and before @
                        import re
                        pattern = r'\]\s*([A-Za-z]+)\s*@'
                        match_result = re.search(pattern, desc)
                        if match_result:
                            selection_match = match_result.group(1).strip().lower()
                            logger.info(f"  Extracted from description (regex): '{selection_match}'")
                        else:
                            # Fallback to string search
                            if 'home @' in desc_lower or '] home' in desc_lower:
                                selection_match = 'home'
                            elif 'away @' in desc_lower or '] away' in desc_lower:
                                selection_match = 'away'
                            elif 'draw @' in desc_lower or '] draw' in desc_lower:
                                selection_match = 'draw'
                            logger.info(f"  Extracted from description (fallback): '{selection_match}'")
                    
                    # Check if won
                    if selection_match:
                        actual_result = 'home' if match.home_score > match.away_score else ('away' if match.away_score > match.home_score else 'draw')
                        logger.info(f"  Comparing: User picked '{selection_match}' vs Actual '{actual_result}'")
                        
                        if match.home_score > match.away_score and selection_match == 'home':
                            is_won = True
                            logger.info(f"  ✓ WON: Home team won with {match.home_score}-{match.away_score}")
                        elif match.away_score > match.home_score and selection_match == 'away':
                            is_won = True
                            logger.info(f"  ✓ WON: Away team won with {match.home_score}-{match.away_score}")
                        elif match.home_score == match.away_score and selection_match == 'draw':
                            is_won = True
                            logger.info(f"  ✓ WON: Match drawn at {match.home_score}-{match.away_score}")
                        else:
                            logger.info(f"  ✗ LOST: User picked {selection_match} but result was {actual_result}")
                    else:
                        logger.warning(f"  ⚠ Could not extract selection from bet {bet.id}")
                
                # Handle Over/Under markets
                elif 'over/under' in desc_lower or market.lower() in ['ou1', 'ou2', 'ou3']:
                    bet_matched = True
                    total_goals = match.home_score + match.away_score
                    
                    # Determine which line and direction
                    is_over = False
                    line = None
                    
                    # Check selection field first (e.g., 'over2', 'under2', 'over1', 'under3')
                    if selection:
                        sel_lower = selection.lower()
                        if sel_lower in ['over1', 'over 1.5']:
                            is_over = True
                            line = 1.5
                        elif sel_lower in ['under1', 'under 1.5']:
                            is_over = False
                            line = 1.5
                        elif sel_lower in ['over2', 'over 2.5']:
                            is_over = True
                            line = 2.5
                        elif sel_lower in ['under2', 'under 2.5']:
                            is_over = False
                            line = 2.5
                        elif sel_lower in ['over3', 'over 3.5']:
                            is_over = True
                            line = 3.5
                        elif sel_lower in ['under3', 'under 3.5']:
                            is_over = False
                            line = 3.5
                    
                    # Parse from description if not found in selection
                    if line is None:
                        import re
                        # Look for patterns like "OVER2" or "Under 1.5" or "OVER 2.5"
                        pattern = r'(OVER|UNDER|Over|Under)\s*(\d)(?:\s*\.5)?'
                        match_ou = re.search(pattern, desc)
                        if match_ou:
                            is_over = match_ou.group(1).lower() == 'over'
                            line_num = int(match_ou.group(2))
                            line = line_num + 0.5
                    
                    logger.info(f"Over/Under bet - Total goals: {total_goals}, Is Over: {is_over}, Line: {line}, Selection: '{selection}', Description: {desc}")
                    
                    if line:
                        if is_over and total_goals > line:
                            is_won = True
                            logger.info(f"Over {line} WON - {total_goals} > {line}")
                        elif not is_over and total_goals < line:
                            is_won = True
                            logger.info(f"Under {line} WON - {total_goals} < {line}")
                        else:
                            logger.info(f"Over/Under LOST - {total_goals} {'>' if is_over else '<'} {line} = False")
                
                # Handle Both Teams Score (GG/NG)
                elif 'both teams score' in desc_lower or 'btts' in desc_lower or market.lower() == 'gg':
                    bet_matched = True
                    both_scored = match.home_score > 0 and match.away_score > 0
                    logger.info(f"BTTS bet - Both scored: {both_scored}, Description: {desc}")
                    if ('yes' in desc_lower or ' gg ' in desc_lower) and both_scored:
                        is_won = True
                    elif ('no' in desc_lower or ' ng ' in desc_lower) and not both_scored:
                        is_won = True
                
                # Handle Correct Score
                elif 'correct score' in desc_lower or 'cs' in market.lower():
                    bet_matched = True
                    score_pattern = f"{match.home_score}-{match.away_score}"
                    logger.info(f"Correct Score bet - Looking for: {score_pattern}, Description: {desc}")
                    if score_pattern in desc:
                        is_won = True
                
                # Handle HT/FT (Half Time/Full Time)
                elif 'half time/full time' in desc_lower or 'htft' in market.lower() or 'ht/ft' in desc_lower:
                    bet_matched = True
                    if match.ht_home_score is not None and match.ht_away_score is not None:
                        # Determine HT result
                        if match.ht_home_score > match.ht_away_score:
                            ht_result = 'h'
                        elif match.ht_away_score > match.ht_home_score:
                            ht_result = 'a'
                        else:
                            ht_result = 'd'
                        
                        # Determine FT result
                        if match.home_score > match.away_score:
                            ft_result = 'h'
                        elif match.away_score > match.home_score:
                            ft_result = 'a'
                        else:
                            ft_result = 'd'
                        
                        actual_result = f"{ht_result}{ft_result}"
                        
                        # Check if bet matches (e.g., "hh", "ad", "dd")
                        if f' {actual_result} @' in desc_lower or f'] {actual_result} @' in desc_lower:
                            is_won = True
                
                # Handle Double Chance
                elif 'double chance' in desc_lower or 'dc' in market.lower():
                    bet_matched = True
                    logger.info(f"Double Chance bet - Home:{match.home_score}, Away:{match.away_score}, Description:{desc}")
                    if match.home_score > match.away_score:
                        # Home win
                        if '1x' in desc_lower or 'home/draw' in desc_lower:
                            is_won = True
                        elif '12' in desc_lower or 'home/away' in desc_lower:
                            is_won = True
                    elif match.away_score > match.home_score:
                        # Away win
                        if 'x2' in desc_lower or 'draw/away' in desc_lower:
                            is_won = True
                        elif '12' in desc_lower or 'home/away' in desc_lower:
                            is_won = True
                    else:
                        # Draw
                        if '1x' in desc_lower or 'home/draw' in desc_lower:
                            is_won = True
                        elif 'x2' in desc_lower or 'draw/away' in desc_lower:
                            is_won = True
                
                # Log if bet type wasn't recognized
                if not bet_matched:
                    logger.warning(f"Could not determine bet type for bet {bet.id}: {desc}")
                
                # Apply result
                logger.info(f"Bet {bet.id} result: {'WON' if is_won else 'LOST'}, Matched type: {bet_matched}")
                if is_won:
                    bet.status = BetStatus.WON.value
                    bet.result = 'win'
                    bet.settled_payout = bet.potential_payout
                    bet.user.balance += bet.settled_payout
                else:
                    bet.status = BetStatus.LOST.value
                    bet.result = 'loss'
                    bet.settled_payout = 0
                
                bet.settled_at = datetime.utcnow()
                settled_count += 1
            
            logger.info(f"Admin {user.username} settled {settled_count} bets for match {match_id}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Match result updated successfully',
            'match': match.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[Update Match Result] Error: {e}")
        db.session.rollback()
        return jsonify({'message': f'Error updating match result: {str(e)}'}), 500

# --- Delete Match ---
@admin_bp.route('/matches/<int:match_id>', methods=['DELETE'])
@admin_required
def delete_match(user, match_id):
    """Delete a match (only if no bets placed, or force delete with bets)"""
    try:
        match = db.session.get(Match, match_id)
        if not match:
            return jsonify({'message': 'Match not found'}), 404
        
        if not match.is_manual:
            return jsonify({'message': 'Cannot delete API-based matches'}), 403
        
        # Check if force delete is requested
        force = request.args.get('force', 'false').lower() == 'true'
        
        # Check if there are any bets on this match
        bet_count = Bet.query.filter_by(match_id=match_id).count()
        if bet_count > 0 and not force:
            # Return bet IDs for debugging
            bet_ids = [b.id for b in Bet.query.filter_by(match_id=match_id).all()]
            return jsonify({
                'message': f'Cannot delete match with {bet_count} existing bet(s)',
                'bet_count': bet_count,
                'bet_ids': bet_ids,
                'can_force': True
            }), 400
        
        # If force delete, remove all bets first
        if force and bet_count > 0:
            Bet.query.filter_by(match_id=match_id).delete()
            logger.warning(f"Admin {user.username} force-deleted {bet_count} bets for match {match_id}")
        
        db.session.delete(match)
        db.session.commit()
        
        logger.info(f"Admin {user.username} deleted match {match_id}")
        
        return jsonify({'message': 'Match deleted successfully'}), 200
    except Exception as e:
        logger.error(f"[Delete Match] Error: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': f'Error deleting match: {str(e)}'}), 500


# --- USER MANAGEMENT ---

@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
@admin_required
def suspend_user(user, user_id):
    """Suspend a user account (put on hold)"""
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404
        
        if target_user.is_admin:
            return jsonify({'message': 'Cannot suspend admin accounts'}), 403
        
        target_user.is_active = False
        db.session.commit()
        
        logger.info(f"Admin {user.username} suspended user {target_user.username} (ID: {user_id})")
        
        return jsonify({
            'message': f'User {target_user.username} has been suspended',
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'is_active': target_user.is_active
            }
        }), 200
    except Exception as e:
        logger.error(f"[Suspend User] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error suspending user'}), 500


@admin_bp.route('/users/<int:user_id>/unsuspend', methods=['POST'])
@admin_required
def unsuspend_user(user, user_id):
    """Unsuspend a user account (reactivate)"""
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404
        
        target_user.is_active = True
        db.session.commit()
        
        logger.info(f"Admin {user.username} unsuspended user {target_user.username} (ID: {user_id})")
        
        return jsonify({
            'message': f'User {target_user.username} has been reactivated',
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'is_active': target_user.is_active
            }
        }), 200
    except Exception as e:
        logger.error(f"[Unsuspend User] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error unsuspending user'}), 500


@admin_bp.route('/users/<int:user_id>/bets', methods=['GET'])
@admin_required
def get_user_bets(user, user_id):
    """Get all bets for a specific user"""
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status = request.args.get('status')  # Optional filter by status
        
        query = Bet.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        bets = query.order_by(Bet.created_at.desc()).paginate(page=page, per_page=per_page)
        
        bets_data = []
        for bet in bets.items:
            # Determine if it's a multi-bet based on booking_code or event_description
            is_multi = bet.booking_code is not None or 'Multi' in bet.event_description or 'Premium' in bet.event_description
            
            bet_data = {
                'id': bet.id,
                'amount': bet.amount,
                'odds': bet.odds,
                'potential_payout': bet.potential_payout,
                'status': bet.status,
                'result': bet.result,
                'created_at': bet.created_at.isoformat(),
                'settled_at': bet.settled_at.isoformat() if bet.settled_at else None,
                'settled_payout': bet.settled_payout,
                'selection': bet.selection,
                'event_description': bet.event_description,
                'is_multi_bet': is_multi,
                'booking_code': bet.booking_code
            }
            
            # Add match info if single bet
            if bet.match:
                bet_data['match'] = {
                    'id': bet.match.id,
                    'home_team': bet.match.home_team,
                    'away_team': bet.match.away_team,
                    'league': bet.match.league,
                    'status': bet.match.status,
                    'home_score': bet.match.home_score,
                    'away_score': bet.match.away_score,
                    'match_time': bet.match.match_time.isoformat() if bet.match.match_time else None
                }
            
            bets_data.append(bet_data)
        
        return jsonify({
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'email': target_user.email
            },
            'bets': bets_data,
            'total': bets.total,
            'pages': bets.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        logger.error(f"[Get User Bets] Error: {e}")
        return jsonify({'message': 'Error fetching user bets'}), 500


@admin_bp.route('/bets/<int:bet_id>/void', methods=['POST'])
@admin_required
def void_bet(user, bet_id):
    """Void a bet and refund the user"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Admin void')
        
        bet = db.session.get(Bet, bet_id)
        if not bet:
            return jsonify({'message': 'Bet not found'}), 404
        
        # Only void active or pending bets
        if bet.status not in [BetStatus.ACTIVE.value, BetStatus.PENDING.value]:
            return jsonify({'message': f'Cannot void bet with status: {bet.status}'}), 400
        
        # Get the user
        bet_user = bet.user
        original_amount = bet.amount
        
        # Refund the amount
        bet_user.balance += original_amount
        
        # Update bet status
        bet.status = BetStatus.VOIDED.value
        bet.result = 'voided'
        bet.settled_at = datetime.utcnow()
        bet.settled_payout = 0.0
        
        db.session.commit()
        
        logger.info(f"Admin {user.username} voided bet {bet_id} for user {bet_user.username}. Refunded: {original_amount} BTC. Reason: {reason}")
        
        return jsonify({
            'message': f'Bet voided successfully. Refunded {original_amount} BTC to {bet_user.username}',
            'bet': {
                'id': bet.id,
                'status': bet.status,
                'result': bet.result,
                'refunded_amount': original_amount
            },
            'user': {
                'id': bet_user.id,
                'username': bet_user.username,
                'new_balance': bet_user.balance
            }
        }), 200
    except Exception as e:
        logger.error(f"[Void Bet] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error voiding bet'}), 500


@admin_bp.route('/bets/<int:bet_id>/cancel', methods=['POST'])
@admin_required  
def cancel_bet(user, bet_id):
    """Cancel a bet (alias for void)"""
    return void_bet(user, bet_id)


@admin_bp.route('/users/<int:user_id>/freeze-betting', methods=['POST'])
@admin_required
def freeze_user_betting(user, user_id):
    """Prevent a user from placing new bets while keeping account active"""
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404
        
        if target_user.is_admin:
            return jsonify({'message': 'Cannot freeze admin accounts'}), 403
        
        # We'll use a new field or mark existing bets
        # For now, suspend the account
        target_user.is_active = False
        db.session.commit()
        
        logger.info(f"Admin {user.username} froze betting for user {target_user.username} (ID: {user_id})")
        
        return jsonify({
            'message': f'Betting frozen for user {target_user.username}',
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'is_active': target_user.is_active
            }
        }), 200
    except Exception as e:
        logger.error(f"[Freeze Betting] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error freezing betting'}), 500


@admin_bp.route('/users/<int:user_id>/payment-info', methods=['GET'])
@admin_required
def get_user_payment_info(user, user_id):
    """Get a user's payment and withdrawal information"""
    try:
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404
        
        payment_info = {
            'user_id': target_user.id,
            'username': target_user.username,
            'email': target_user.email,
            'balance': target_user.balance,
            'withdrawal_wallet': target_user.withdrawal_wallet,
            'bank_account_name': target_user.bank_account_name,
            'bank_account_number': target_user.bank_account_number,
            'bank_name': target_user.bank_name,
            'paypal_email': target_user.paypal_email,
            'skrill_email': target_user.skrill_email,
            'usdt_wallet': target_user.usdt_wallet,
            'payment_notes': target_user.payment_notes
        }
        
        logger.info(f"Admin {user.username} viewed payment info for user {target_user.username} (ID: {user_id})")
        
        return jsonify({'payment_info': payment_info}), 200
    except Exception as e:
        logger.error(f"[Get Payment Info] Error: {e}")
        return jsonify({'message': 'Error retrieving payment information'}), 500


@admin_bp.route('/users/<int:user_id>/payment-info', methods=['PUT'])
@admin_required
def update_user_payment_info(user, user_id):
    """Update a user's payment and withdrawal information"""
    try:
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.json
        
        # Update payment fields if provided
        if 'withdrawal_wallet' in data:
            target_user.withdrawal_wallet = data['withdrawal_wallet']
        if 'bank_account_name' in data:
            target_user.bank_account_name = data['bank_account_name']
        if 'bank_account_number' in data:
            target_user.bank_account_number = data['bank_account_number']
        if 'bank_name' in data:
            target_user.bank_name = data['bank_name']
        if 'paypal_email' in data:
            target_user.paypal_email = data['paypal_email']
        if 'skrill_email' in data:
            target_user.skrill_email = data['skrill_email']
        if 'usdt_wallet' in data:
            target_user.usdt_wallet = data['usdt_wallet']
        if 'payment_notes' in data:
            target_user.payment_notes = data['payment_notes']
        
        db.session.commit()
        
        logger.info(f"Admin {user.username} updated payment info for user {target_user.username} (ID: {user_id})")
        
        return jsonify({
            'message': 'Payment information updated successfully',
            'payment_info': {
                'user_id': target_user.id,
                'username': target_user.username,
                'withdrawal_wallet': target_user.withdrawal_wallet,
                'bank_account_name': target_user.bank_account_name,
                'bank_account_number': target_user.bank_account_number,
                'bank_name': target_user.bank_name,
                'paypal_email': target_user.paypal_email,
                'skrill_email': target_user.skrill_email,
                'usdt_wallet': target_user.usdt_wallet,
                'payment_notes': target_user.payment_notes
            }
        }), 200
    except Exception as e:
        logger.error(f"[Update Payment Info] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error updating payment information'}), 500


@admin_bp.route('/payments/submissions', methods=['GET'])
@admin_required
def get_payment_submissions(user):
    """Get all deposit/withdrawal payment submissions with details"""
    try:
        
        # Get query parameters
        status = request.args.get('status')
        user_id = request.args.get('user_id')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = DepositRequest.query
        
        if status:
            query = query.filter_by(status=status)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # Order by most recent first
        query = query.order_by(DepositRequest.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        submissions = []
        for deposit in pagination.items:
            submission_data = deposit.to_dict()
            
            # Add user details
            deposit_user = User.query.get(deposit.user_id)
            if deposit_user:
                submission_data['user_details'] = {
                    'username': deposit_user.username,
                    'email': deposit_user.email,
                    'balance': deposit_user.balance,
                    'withdrawal_wallet': deposit_user.withdrawal_wallet,
                    'bank_account_name': deposit_user.bank_account_name,
                    'bank_account_number': deposit_user.bank_account_number,
                    'bank_name': deposit_user.bank_name,
                    'paypal_email': deposit_user.paypal_email
                }
            
            submissions.append(submission_data)
        
        logger.info(f"Admin {user.username} viewed payment submissions (page {page})")
        
        return jsonify({
            'submissions': submissions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
    except Exception as e:
        logger.error(f"[Get Payment Submissions] Error: {e}")
        return jsonify({'message': 'Error retrieving payment submissions'}), 500


# ===== PLATFORM PAYMENT METHODS MANAGEMENT =====

@admin_bp.route('/payment-methods', methods=['GET'])
@admin_required
def get_payment_methods(user):
    """Get all platform payment methods (where users deposit)"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        query = PaymentMethod.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        methods = query.order_by(PaymentMethod.method_type, PaymentMethod.created_at.desc()).all()
        
        return jsonify({
            'payment_methods': [method.to_dict() for method in methods]
        }), 200
    except Exception as e:
        logger.error(f"[Get Payment Methods] Error: {e}")
        return jsonify({'message': 'Error retrieving payment methods'}), 500


@admin_bp.route('/payment-methods', methods=['POST'])
@admin_required
def create_payment_method(user):
    """Create a new platform payment method"""
    try:
        data = request.json
        
        if not data.get('method_type') or not data.get('method_name'):
            return jsonify({'message': 'method_type and method_name are required'}), 400
        
        method = PaymentMethod(
            method_type=data['method_type'],
            method_name=data['method_name'],
            is_active=data.get('is_active', True),
            wallet_address=data.get('wallet_address'),
            usdt_wallet_address=data.get('usdt_wallet_address'),
            usdt_network=data.get('usdt_network'),
            account_name=data.get('account_name'),
            account_number=data.get('account_number'),
            bank_name=data.get('bank_name'),
            swift_code=data.get('swift_code'),
            email=data.get('email'),
            phone=data.get('phone'),
            qr_code=data.get('qr_code'),
            instructions=data.get('instructions'),
            created_by=user.id
        )
        
        db.session.add(method)
        db.session.commit()
        
        logger.info(f"Admin {user.username} created payment method: {method.method_name}")
        
        return jsonify({
            'message': 'Payment method created successfully',
            'payment_method': method.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"[Create Payment Method] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error creating payment method'}), 500


@admin_bp.route('/payment-methods/<int:method_id>', methods=['GET'])
@admin_required
def get_payment_method(user, method_id):
    """Get a specific payment method"""
    try:
        method = PaymentMethod.query.get(method_id)
        if not method:
            return jsonify({'message': 'Payment method not found'}), 404
        
        return jsonify({'payment_method': method.to_dict()}), 200
    except Exception as e:
        logger.error(f"[Get Payment Method] Error: {e}")
        return jsonify({'message': 'Error retrieving payment method'}), 500


@admin_bp.route('/payment-methods/<int:method_id>', methods=['PUT'])
@admin_required
def update_payment_method(user, method_id):
    """Update a platform payment method"""
    try:
        method = PaymentMethod.query.get(method_id)
        if not method:
            return jsonify({'message': 'Payment method not found'}), 404
        
        data = request.json
        
        # Update fields if provided
        if 'method_type' in data:
            method.method_type = data['method_type']
        if 'method_name' in data:
            method.method_name = data['method_name']
        if 'is_active' in data:
            method.is_active = data['is_active']
        if 'wallet_address' in data:
            method.wallet_address = data['wallet_address']
        if 'usdt_wallet_address' in data:
            method.usdt_wallet_address = data['usdt_wallet_address']
        if 'usdt_network' in data:
            method.usdt_network = data['usdt_network']
        if 'account_name' in data:
            method.account_name = data['account_name']
        if 'account_number' in data:
            method.account_number = data['account_number']
        if 'bank_name' in data:
            method.bank_name = data['bank_name']
        if 'swift_code' in data:
            method.swift_code = data['swift_code']
        if 'email' in data:
            method.email = data['email']
        if 'phone' in data:
            method.phone = data['phone']
        if 'qr_code' in data:
            method.qr_code = data['qr_code']
        if 'instructions' in data:
            method.instructions = data['instructions']
        
        db.session.commit()
        
        logger.info(f"Admin {user.username} updated payment method: {method.method_name} (ID: {method_id})")
        
        return jsonify({
            'message': 'Payment method updated successfully',
            'payment_method': method.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[Update Payment Method] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error updating payment method'}), 500


@admin_bp.route('/payment-methods/<int:method_id>', methods=['DELETE'])
@admin_required
def delete_payment_method(user, method_id):
    """Delete a platform payment method"""
    try:
        method = PaymentMethod.query.get(method_id)
        if not method:
            return jsonify({'message': 'Payment method not found'}), 404
        
        method_name = method.method_name
        db.session.delete(method)
        db.session.commit()
        
        logger.info(f"Admin {user.username} deleted payment method: {method_name} (ID: {method_id})")
        
        return jsonify({'message': f'Payment method "{method_name}" deleted successfully'}), 200
    except Exception as e:
        logger.error(f"[Delete Payment Method] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error deleting payment method'}), 500


@admin_bp.route('/payment-methods/<int:method_id>/toggle', methods=['POST'])
@admin_required
def toggle_payment_method(user, method_id):
    """Toggle payment method active status"""
    try:
        method = PaymentMethod.query.get(method_id)
        if not method:
            return jsonify({'message': 'Payment method not found'}), 404
        
        method.is_active = not method.is_active
        db.session.commit()
        
        status = 'activated' if method.is_active else 'deactivated'
        logger.info(f"Admin {user.username} {status} payment method: {method.method_name}")
        
        return jsonify({
            'message': f'Payment method {status} successfully',
            'payment_method': method.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[Toggle Payment Method] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error toggling payment method'}), 500

