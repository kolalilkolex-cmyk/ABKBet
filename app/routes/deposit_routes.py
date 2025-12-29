"""Deposit routes with manual approval system"""
from flask import Blueprint, request, jsonify
from app.models import db, User
from app.models.deposit import DepositRequest
from app.utils.decorators import token_required, admin_required
from app.payment_methods import get_payment_method, get_enabled_payment_methods
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
deposit_bp = Blueprint('deposit', __name__, url_prefix='/api/deposit')

@deposit_bp.route('/methods', methods=['GET'])
def get_payment_methods():
    """Get available payment methods and their details"""
    try:
        methods = get_enabled_payment_methods()
        return jsonify({'methods': methods}), 200
    except Exception as e:
        logger.error(f"Error fetching payment methods: {e}")
        return jsonify({'message': 'Error fetching payment methods'}), 500

@deposit_bp.route('/method/<method_id>', methods=['GET'])
def get_payment_method_details(method_id):
    """Get specific payment method details"""
    try:
        method = get_payment_method(method_id)
        if not method:
            return jsonify({'message': 'Payment method not found'}), 404
        
        if not method.get('enabled', False):
            return jsonify({'message': 'Payment method is currently disabled'}), 400
        
        return jsonify({'method': method}), 200
    except Exception as e:
        logger.error(f"Error fetching payment method: {e}")
        return jsonify({'message': 'Error fetching payment method'}), 500

@deposit_bp.route('/request', methods=['POST'])
@token_required
def create_deposit_request(user):
    """User submits a deposit request for admin approval"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        transaction_reference = data.get('transaction_reference')
        payment_proof = data.get('payment_proof')  # Optional screenshot URL
        
        if not all([amount, payment_method, transaction_reference]):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Validate payment method
        method_config = get_payment_method(payment_method)
        if not method_config or not method_config.get('enabled', False):
            return jsonify({'message': 'Invalid or disabled payment method'}), 400
        
        # Validate amount
        amount = float(amount)
        min_deposit = method_config.get('min_deposit', 10)
        max_deposit = method_config.get('max_deposit', 10000)
        
        if amount < min_deposit:
            return jsonify({'message': f'Minimum deposit is ${min_deposit}'}), 400
        if amount > max_deposit:
            return jsonify({'message': f'Maximum deposit is ${max_deposit}'}), 400
        
        # Create deposit request
        deposit_request = DepositRequest(
            user_id=user.id,
            amount=amount,
            payment_method=payment_method,
            transaction_reference=transaction_reference,
            payment_proof=payment_proof,
            status='pending'
        )
        
        db.session.add(deposit_request)
        db.session.commit()
        
        return jsonify({
            'message': 'Deposit request submitted successfully. Admin will review and approve shortly.',
            'deposit_id': deposit_request.id,
            'status': 'pending'
        }), 201
        
    except Exception as e:
        logger.error(f"Deposit request error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error processing deposit request'}), 500

@deposit_bp.route('/my-requests', methods=['GET'])
@token_required
def get_my_deposit_requests(user):
    """Get current user's deposit requests"""
    try:
        requests = DepositRequest.query.filter_by(user_id=user.id)\
            .order_by(DepositRequest.created_at.desc()).all()
        
        return jsonify({
            'deposits': [req.to_dict() for req in requests]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching deposit requests: {e}")
        return jsonify({'message': 'Error fetching deposit requests'}), 500

@deposit_bp.route('/pending', methods=['GET'])
@admin_required
def get_pending_deposits(user):
    """Admin: Get all pending deposit requests"""
    try:
        pending = DepositRequest.query.filter_by(status='pending')\
            .order_by(DepositRequest.created_at.asc()).all()
        
        return jsonify({
            'deposits': [req.to_dict() for req in pending],
            'total': len(pending)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching pending deposits: {e}")
        return jsonify({'message': 'Error fetching pending deposits'}), 500

@deposit_bp.route('/all', methods=['GET'])
@admin_required
def get_all_deposits(user):
    """Admin: Get all deposit requests with optional status filter"""
    try:
        status = request.args.get('status')  # pending, approved, rejected
        
        query = DepositRequest.query
        if status:
            query = query.filter_by(status=status)
        
        deposits = query.order_by(DepositRequest.created_at.desc()).all()
        
        return jsonify({
            'deposits': [req.to_dict() for req in deposits],
            'total': len(deposits)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching deposits: {e}")
        return jsonify({'message': 'Error fetching deposits'}), 500

@deposit_bp.route('/approve/<int:deposit_id>', methods=['POST'])
@admin_required
def approve_deposit(user, deposit_id):
    """Admin: Approve a deposit request and credit user's balance"""
    try:
        deposit_request = DepositRequest.query.get(deposit_id)
        
        if not deposit_request:
            return jsonify({'message': 'Deposit request not found'}), 404
        
        if deposit_request.status != 'pending':
            return jsonify({'message': 'Deposit already processed'}), 400
        
        # Get the user who made the deposit
        deposit_user = User.query.get(deposit_request.user_id)
        if not deposit_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Credit user's balance in USD
        deposit_user.balance += deposit_request.amount
        
        # Update deposit request
        deposit_request.status = 'approved'
        deposit_request.approved_by = user.id
        deposit_request.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Deposit approved and credited successfully',
            'user_id': deposit_user.id,
            'username': deposit_user.username,
            'amount_usd': deposit_request.amount,
            'new_balance_usd': deposit_user.balance
        }), 200
        
    except Exception as e:
        logger.error(f"Deposit approval error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error approving deposit'}), 500

@deposit_bp.route('/reject/<int:deposit_id>', methods=['POST'])
@admin_required
def reject_deposit(user, deposit_id):
    """Admin: Reject a deposit request"""
    try:
        data = request.get_json()
        admin_notes = data.get('admin_notes', 'Deposit rejected by admin')
        
        deposit_request = DepositRequest.query.get(deposit_id)
        
        if not deposit_request:
            return jsonify({'message': 'Deposit request not found'}), 404
        
        if deposit_request.status != 'pending':
            return jsonify({'message': 'Deposit already processed'}), 400
        
        # Update deposit request
        deposit_request.status = 'rejected'
        deposit_request.approved_by = user.id
        deposit_request.admin_notes = admin_notes
        deposit_request.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Deposit rejected',
            'deposit_id': deposit_id,
            'reason': admin_notes
        }), 200
        
    except Exception as e:
        logger.error(f"Deposit rejection error: {e}")
        db.session.rollback()
        return jsonify({'message': 'Error rejecting deposit'}), 500
