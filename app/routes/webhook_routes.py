"""
Payment Webhook Handler for transaction confirmations
Process incoming webhook notifications from payment providers
"""

import os
from flask import Blueprint, request, jsonify
from app.models import db, Transaction, User
from app.services.payment_core import PaymentCore
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)
webhook_bp = Blueprint('webhook', __name__, url_prefix='/api/webhook')
payment_service = PaymentCore(bitcoin_network='testnet')

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    expected_sig = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_sig)

@webhook_bp.route('/transaction-confirmation', methods=['POST'])
def transaction_confirmation():
    """Handle transaction confirmation webhook"""
    try:
        # Verify signature
        signature = request.headers.get('X-Signature')
        secret = os.getenv('WEBHOOK_SECRET', 'webhook-secret')
        
        if not signature or not verify_webhook_signature(request.data.decode(), signature, secret):
            logger.warning("Invalid webhook signature")
            return jsonify({'message': 'Invalid signature'}), 401
        
        data = request.get_json()
        
        if not data or not data.get('tx_hash'):
            return jsonify({'message': 'Missing tx_hash'}), 400
        
        # Update transaction confirmations
        transaction = Transaction.query.filter_by(tx_hash=data['tx_hash']).first()
        
        if not transaction:
            logger.warning(f"Transaction not found: {data['tx_hash']}")
            return jsonify({'message': 'Transaction not found'}), 404
        
        # Update confirmation count
        confirmations = data.get('confirmations', 0)
        transaction.confirmations = confirmations
        
        # Mark as confirmed if threshold met
        if confirmations >= 1:  # Configurable threshold
            transaction.status = 'confirmed'
            logger.info(f"Transaction confirmed: {transaction.tx_hash}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook processed',
            'confirmations': confirmations
        }), 200
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'message': 'Error processing webhook'}), 500

@webhook_bp.route('/block-confirmation', methods=['POST'])
def block_confirmation():
    """Handle new block confirmation webhook"""
    try:
        data = request.get_json()
        
        # Process all pending transactions
        pending_txs = Transaction.query.filter_by(status='pending').all()
        
        confirmed_count = 0
        for tx in pending_txs:
            # Verify each transaction
            success = payment_service.verify_and_confirm_transaction(tx.tx_hash)
            if success:
                confirmed_count += 1
        
        logger.info(f"Processed {confirmed_count} confirmed transactions from block")
        
        return jsonify({
            'message': 'Block processed',
            'confirmed': confirmed_count
        }), 200
    
    except Exception as e:
        logger.error(f"Block webhook error: {e}")
        return jsonify({'message': 'Error processing block'}), 500
