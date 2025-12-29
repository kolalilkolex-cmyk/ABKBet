print("📂 payment_routes.py is loading")
from flask import Blueprint, request, jsonify
from app.models import db, User
from app.models.payment_method import PaymentMethod
from app.services.payment_core import PaymentCore
from app.utils.decorators import token_required
from app.utils.currency import btc_to_usd
import logging
print("📦 PaymentCore imported from:", PaymentCore.__module__)

logger = logging.getLogger(__name__)
payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')
payment_service = PaymentCore(bitcoin_network='testnet')

@payment_bp.route('/methods', methods=['GET'])
def get_available_payment_methods():
    """Get all active payment methods (public endpoint for users)"""
    try:
        methods = PaymentMethod.query.filter_by(is_active=True).order_by(PaymentMethod.method_type).all()
        return jsonify({
            'payment_methods': [method.to_dict() for method in methods]
        }), 200
    except Exception as e:
        logger.error(f"[Get Payment Methods] Error: {e}")
        return jsonify({'message': 'Error fetching payment methods'}), 500

@payment_bp.route('/wallet', methods=['GET'])
@token_required
def get_wallet(user):
    """Get user's wallet information"""
    try:
        wallet = payment_service.get_or_create_wallet(user)  # This should internally call BitcoinService.generate_address()
        return jsonify({
            'wallet': {
                'bitcoin_address': wallet.bitcoin_address,
                'total_received': wallet.total_received,
                'total_sent': wallet.total_sent,
                'created_at': wallet.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        logger.error(f"Wallet fetch error: {e}")
        return jsonify({'message': 'Error fetching wallet'}), 500
        
@payment_bp.route('/balance', methods=['GET'])
@token_required
def get_balance(user):
    """Get user's balance in USD"""
    try:
        balance = user.balance if user.balance else 0.0
        return jsonify({
            'balance_usd': balance,
            'balance': balance,  # For UI display
            'currency': 'USD'
        }), 200
    except Exception as e:
        logger.error(f"Balance fetch error: {e}")
        return jsonify({'message': 'Error fetching balance'}), 500

@payment_bp.route('/deposit', methods=['POST'])
@token_required
def deposit(user):
    """Verify and record a Bitcoin deposit"""
    try:
        data = request.get_json()
        tx_hash = data.get('tx_hash')
        amount = data.get('amount')

        if not tx_hash or not amount:
            return jsonify({'message': 'Missing tx_hash or amount'}), 400

        # Get user's wallet address
        wallet = payment_service.get_or_create_wallet(user)
        address = wallet.bitcoin_address

        # Verify transaction on blockchain
        confirmed = payment_service.bitcoin_service.verify_transaction(
            tx_hash=tx_hash,
            expected_amount=float(amount),
            expected_address=address,
            required_confirmations=1
        )

        if not confirmed:
            return jsonify({'message': 'Transaction not confirmed or invalid'}), 400

        # Process deposit
        success = payment_service.process_deposit(
            user=user,
            tx_hash=tx_hash,
            amount=float(amount)
        )

        if success:
            return jsonify({
                'message': 'Deposit verified and processed',
                'balance': user.balance
            }), 200
        else:
            return jsonify({'message': 'Failed to record deposit'}), 500

    except Exception as e:
        logger.error(f"Deposit error: {e}")
        db.session.rollback()
        return jsonify({'message': 'An error occurred during deposit'}), 500
    
@payment_bp.route('/withdraw', methods=['POST'])
@token_required
def withdraw(user):
    """Initiate a Bitcoin withdrawal"""
    try:
        data = request.get_json()
        
        if not data or not data.get('to_address') or not data.get('amount'):
            return jsonify({'message': 'Missing to_address or amount'}), 400
        
        success = payment_service.create_withdrawal_transaction(
            user=user,
            to_address=data['to_address'],
            amount=float(data['amount'])
        )
        
        if success:
            return jsonify({
                'message': 'Withdrawal initiated',
                'balance': user.balance
            }), 200
        else:
            return jsonify({'message': 'Failed to initiate withdrawal'}), 400
    
    except Exception as e:
        logger.error(f"Withdrawal error: {e}")
        db.session.rollback()
        return jsonify({'message': 'An error occurred during withdrawal'}), 500

@payment_bp.route('/transactions', methods=['GET'])
@token_required
def get_transactions(user):
    """Get user's transaction history"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        transactions = payment_service.get_transaction_history(user, limit=limit)
        
        return jsonify({
            'transactions': [{
                'id': tx.id,
                'tx_hash': tx.tx_hash,
                'amount_btc': tx.amount,
                'amount_usd': btc_to_usd(tx.amount),
                'amount': btc_to_usd(tx.amount),  # For UI display
                'type': tx.transaction_type,
                'status': tx.status,
                'confirmations': tx.confirmations,
                'from_address': tx.from_address,
                'to_address': tx.to_address,
                'created_at': tx.created_at.isoformat()
            } for tx in transactions]
        }), 200
    except Exception as e:
        logger.error(f"Transaction history error: {e}")
        return jsonify({'message': 'Error fetching transaction history'}), 500

@payment_bp.route('/fee-estimate', methods=['GET'])
def get_fee_estimate():
    """Get current Bitcoin network fees"""
    try:
        fees = payment_service.bitcoin_service.get_fee_estimate()
        return jsonify({
            'fees': fees,
            'unit': 'BTC'
        }), 200
    except Exception as e:
        logger.error(f"Fee estimate error: {e}")
        return jsonify({'message': 'Error fetching fee estimate'}), 500
    
@payment_bp.route('/deposit/skrill', methods=['POST'])
@token_required
def deposit_skrill(user):
    try:
        data = request.get_json()
        reference_id = data.get('reference_id')
        amount = data.get('amount')

        if not reference_id or not amount:
            return jsonify({'message': 'Missing reference_id or amount'}), 400

        success = payment_service.process_skrill_deposit(user, reference_id, float(amount))
        if success:
            return jsonify({'message': 'Skrill deposit processed', 'balance': user.balance}), 200
        else:
            return jsonify({'message': 'Deposit failed'}), 400

    except Exception as e:
        logger.exception(f"Skrill deposit error: {e}")
        return jsonify({'message': 'Deposit failed', 'error': str(e)}), 500
    
@payment_bp.route('/deposit/revolut', methods=['POST'])
@token_required
def deposit_revolut(user):
    try:
        data = request.get_json()
        reference_id = data.get('reference_id')
        amount = data.get('amount')

        if not reference_id or not amount:
            return jsonify({'message': 'Missing reference_id or amount'}), 400

        success = payment_service.process_revolut_deposit(user, reference_id, float(amount))
        if success:
            return jsonify({'message': 'Revolut deposit processed', 'balance': user.balance}), 200
        else:
            return jsonify({'message': 'Deposit failed'}), 400

    except Exception as e:
        logger.error(f"Revolut deposit error: {e}")
        return jsonify({'message': 'Deposit failed'}), 500
    
@payment_bp.route('/deposit/eversend', methods=['POST'])
@token_required
def deposit_eversend(user):
    try:
        data = request.get_json()
        reference_id = data.get('reference_id')
        amount = data.get('amount')

        if not reference_id or not amount:
            return jsonify({'message': 'Missing reference_id or amount'}), 400

        success = payment_service.process_eversend_deposit(user, reference_id, float(amount))
        if success:
            return jsonify({'message': 'Eversend deposit processed', 'balance': user.balance}), 200
        else:
            return jsonify({'message': 'Deposit failed'}), 400

    except Exception as e:
        logger.error(f"Eversend deposit error: {e}")
        return jsonify({'message': 'Deposit failed'}), 500