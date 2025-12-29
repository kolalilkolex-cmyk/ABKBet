"""Withdrawal Request model for manual payment processing"""

from datetime import datetime
from app.extensions import db

class WithdrawalRequest(db.Model):
    """Model for tracking withdrawal requests across all payment methods"""
    __tablename__ = 'withdrawal_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Payment details
    payment_method = db.Column(db.String(50), nullable=False)  # bitcoin, bank_transfer, paypal, skrill, usdt
    amount_usd = db.Column(db.Float, nullable=False)
    
    # Method-specific details stored as JSON-like strings
    payment_details = db.Column(db.Text, nullable=True)  # Store bank/wallet address info
    
    # For bank transfers
    country = db.Column(db.String(50), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    account_name = db.Column(db.String(100), nullable=True)
    
    # For crypto/digital wallets
    wallet_address = db.Column(db.String(255), nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='PENDING')  # PENDING, APPROVED, REJECTED, PROCESSING, COMPLETED
    admin_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='withdrawal_requests')
    processor = db.relationship('User', foreign_keys=[processed_by])
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'payment_method': self.payment_method,
            'amount_usd': self.amount_usd,
            'country': self.country,
            'bank_name': self.bank_name,
            'account_number': self.account_number,
            'account_name': self.account_name,
            'wallet_address': self.wallet_address,
            'payment_details': self.payment_details,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processed_by': self.processed_by
        }
    
    def __repr__(self):
        return f'<WithdrawalRequest {self.id}: {self.user.username if self.user else "Unknown"} - {self.payment_method} ${self.amount_usd}>'
