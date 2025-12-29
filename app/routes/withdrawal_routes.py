"""Withdrawal routes for manual payment processing"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from app.models import User
from app.models.withdrawal_request import WithdrawalRequest
from app.extensions import db
from app.utils.decorators import token_required
from app.payment_methods import get_withdrawal_method, get_enabled_withdrawal_methods

# Admin decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    @token_required
    def wrapper(user, *args, **kwargs):
        if not getattr(user, 'is_admin', False):
            return jsonify({'message': 'Admin access required'}), 403
        return f(user, *args, **kwargs)
    return wrapper

withdrawal_bp = Blueprint('withdrawal', __name__, url_prefix='/api/withdrawal')
logger = logging.getLogger(__name__)

# --- User Withdrawal Routes ---

@withdrawal_bp.route('/methods', methods=['GET'])
@token_required
def get_withdrawal_methods(user):
    """Get available withdrawal methods"""
    try:
        methods = get_enabled_withdrawal_methods()
        return jsonify({
            'methods': methods,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"[Withdrawal Methods] Error: {e}")
        return jsonify({'message': 'Error fetching withdrawal methods'}), 500

@withdrawal_bp.route('/submit', methods=['POST'])
@token_required
def submit_withdrawal(user):
    """Submit a new withdrawal request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('payment_method'):
            return jsonify({'message': 'Payment method is required'}), 400
        if not data.get('amount_usd'):
            return jsonify({'message': 'Amount is required'}), 400
        
        payment_method = data['payment_method']
        amount_usd = float(data['amount_usd'])
        
        # Validate payment method
        method_config = get_withdrawal_method(payment_method)
        if not method_config or not method_config.get('enabled'):
            return jsonify({'message': 'Invalid payment method'}), 400
        
        # Check minimum withdrawal (default $20)
        min_withdrawal = method_config.get('min_withdrawal', 20)
        if amount_usd < min_withdrawal:
            return jsonify({'message': f'Minimum withdrawal is ${min_withdrawal}'}), 400
        
        # Check maximum withdrawal
        max_withdrawal = method_config.get('max_withdrawal', 50000)
        if amount_usd > max_withdrawal:
            return jsonify({'message': f'Maximum withdrawal is ${max_withdrawal}'}), 400
        
        # Check user balance (both in USD)
        if user.balance < amount_usd:
            return jsonify({'message': 'Insufficient balance'}), 400
        
        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            user_id=user.id,
            payment_method=payment_method,
            amount_usd=amount_usd,
            status='PENDING'
        )
        
        # Store method-specific details
        if payment_method == 'bank_transfer':
            withdrawal.country = data.get('country')
            withdrawal.bank_name = data.get('bank_name')
            withdrawal.account_number = data.get('account_number')
            withdrawal.account_name = data.get('account_name')
        elif payment_method in ['bitcoin', 'usdt']:
            withdrawal.wallet_address = data.get('wallet_address')
        elif payment_method in ['paypal', 'skrill']:
            withdrawal.wallet_address = data.get('email')  # Reuse wallet_address for email
        
        withdrawal.payment_details = data.get('notes', '')
        
        # Deduct balance immediately in USD (will be refunded if rejected)
        user.balance -= amount_usd
        
        db.session.add(withdrawal)
        db.session.commit()
        
        logger.info(f"Withdrawal request created: User {user.username}, Method {payment_method}, Amount ${amount_usd}")
        
        return jsonify({
            'message': 'Withdrawal request submitted successfully',
            'withdrawal_id': withdrawal.id,
            'status': 'PENDING',
            'success': True
        }), 201
        
    except ValueError as e:
        return jsonify({'message': 'Invalid amount format'}), 400
    except Exception as e:
        logger.error(f"[Submit Withdrawal] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error submitting withdrawal request'}), 500

@withdrawal_bp.route('/history', methods=['GET'])
@token_required
def get_withdrawal_history(user):
    """Get user's withdrawal history"""
    try:
        withdrawals = WithdrawalRequest.query.filter_by(user_id=user.id).order_by(
            WithdrawalRequest.created_at.desc()
        ).all()
        
        return jsonify({
            'withdrawals': [w.to_dict() for w in withdrawals],
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"[Withdrawal History] Error: {e}")
        return jsonify({'message': 'Error fetching withdrawal history'}), 500

@withdrawal_bp.route('/<int:withdrawal_id>', methods=['GET'])
@token_required
def get_withdrawal_details(user, withdrawal_id):
    """Get details of a specific withdrawal"""
    try:
        withdrawal = WithdrawalRequest.query.filter_by(
            id=withdrawal_id,
            user_id=user.id
        ).first()
        
        if not withdrawal:
            return jsonify({'message': 'Withdrawal not found'}), 404
        
        return jsonify({
            'withdrawal': withdrawal.to_dict(),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"[Withdrawal Details] Error: {e}")
        return jsonify({'message': 'Error fetching withdrawal details'}), 500

# --- Admin Withdrawal Routes ---

@withdrawal_bp.route('/admin/withdrawals', methods=['GET'])
@admin_required
def get_all_withdrawals(user):
    """Get all withdrawal requests (admin only)"""
    try:
        status_filter = request.args.get('status', 'PENDING')
        
        if status_filter == 'all':
            withdrawals = WithdrawalRequest.query.order_by(
                WithdrawalRequest.created_at.desc()
            ).all()
        else:
            withdrawals = WithdrawalRequest.query.filter_by(
                status=status_filter.upper()
            ).order_by(WithdrawalRequest.created_at.desc()).all()
        
        return jsonify({
            'withdrawals': [w.to_dict() for w in withdrawals],
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"[Admin Withdrawals] Error: {e}")
        return jsonify({'message': 'Error fetching withdrawals'}), 500

@withdrawal_bp.route('/admin/withdrawals/<int:withdrawal_id>/approve', methods=['POST'])
@admin_required
def approve_withdrawal(user, withdrawal_id):
    """Approve a withdrawal request (admin only)"""
    try:
        withdrawal = WithdrawalRequest.query.get(withdrawal_id)
        
        if not withdrawal:
            return jsonify({'message': 'Withdrawal not found'}), 404
        
        if withdrawal.status != 'PENDING':
            return jsonify({'message': 'Withdrawal already processed'}), 400
        
        data = request.get_json() or {}
        
        # Update withdrawal status
        withdrawal.status = 'APPROVED'
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.processed_by = user.id
        withdrawal.admin_notes = data.get('notes', '')
        
        # Balance already deducted when request was created
        
        db.session.commit()
        
        logger.info(f"Admin {user.username} approved withdrawal {withdrawal_id}")
        
        return jsonify({
            'message': 'Withdrawal approved successfully',
            'withdrawal': withdrawal.to_dict(),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"[Approve Withdrawal] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error approving withdrawal'}), 500

@withdrawal_bp.route('/admin/withdrawals/<int:withdrawal_id>/reject', methods=['POST'])
@admin_required
def reject_withdrawal(user, withdrawal_id):
    """Reject a withdrawal request (admin only)"""
    try:
        withdrawal = WithdrawalRequest.query.get(withdrawal_id)
        
        if not withdrawal:
            return jsonify({'message': 'Withdrawal not found'}), 404
        
        if withdrawal.status != 'PENDING':
            return jsonify({'message': 'Withdrawal already processed'}), 400
        
        data = request.get_json() or {}
        
        # Refund the amount to user's balance in USD
        withdrawal_user = User.query.get(withdrawal.user_id)
        if withdrawal_user:
            withdrawal_user.balance += withdrawal.amount_usd
        
        # Update withdrawal status
        withdrawal.status = 'REJECTED'
        withdrawal.processed_at = datetime.utcnow()
        withdrawal.processed_by = user.id
        withdrawal.admin_notes = data.get('notes', 'Withdrawal rejected')
        
        db.session.commit()
        
        logger.info(f"Admin {user.username} rejected withdrawal {withdrawal_id}")
        
        return jsonify({
            'message': 'Withdrawal rejected and amount refunded',
            'withdrawal': withdrawal.to_dict(),
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"[Reject Withdrawal] Error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error rejecting withdrawal'}), 500

@withdrawal_bp.route('/admin/withdrawals/stats', methods=['GET'])
@admin_required
def get_withdrawal_stats(user):
    """Get withdrawal statistics (admin only)"""
    try:
        total_pending = WithdrawalRequest.query.filter_by(status='PENDING').count()
        total_approved = WithdrawalRequest.query.filter_by(status='APPROVED').count()
        total_rejected = WithdrawalRequest.query.filter_by(status='REJECTED').count()
        
        pending_amount = db.session.query(db.func.sum(WithdrawalRequest.amount_usd)).filter_by(
            status='PENDING'
        ).scalar() or 0
        
        approved_amount = db.session.query(db.func.sum(WithdrawalRequest.amount_usd)).filter_by(
            status='APPROVED'
        ).scalar() or 0
        
        return jsonify({
            'stats': {
                'pending_count': total_pending,
                'approved_count': total_approved,
                'rejected_count': total_rejected,
                'pending_amount': pending_amount,
                'approved_amount': approved_amount
            },
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"[Withdrawal Stats] Error: {e}")
        return jsonify({'message': 'Error fetching withdrawal stats'}), 500
