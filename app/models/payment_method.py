from app.extensions import db
from datetime import datetime

class PaymentMethod(db.Model):
    """Admin-managed payment methods for receiving deposits"""
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    method_type = db.Column(db.String(50), nullable=False)  # 'bitcoin', 'bank_transfer', 'paypal', etc.
    method_name = db.Column(db.String(100), nullable=False)  # Display name
    is_active = db.Column(db.Boolean, default=True)
    
    # Payment details (flexible for different payment types)
    wallet_address = db.Column(db.String(255), nullable=True)  # For crypto
    usdt_wallet_address = db.Column(db.String(255), nullable=True)  # For USDT specifically
    usdt_network = db.Column(db.String(50), nullable=True)  # TRC20, ERC20, BEP20, etc.
    account_name = db.Column(db.String(255), nullable=True)  # For bank
    account_number = db.Column(db.String(100), nullable=True)  # For bank
    bank_name = db.Column(db.String(255), nullable=True)  # For bank
    swift_code = db.Column(db.String(50), nullable=True)  # For international bank
    email = db.Column(db.String(255), nullable=True)  # For PayPal, Skrill, etc.
    phone = db.Column(db.String(50), nullable=True)  # For mobile money
    qr_code = db.Column(db.String(500), nullable=True)  # QR code data/URL
    instructions = db.Column(db.Text, nullable=True)  # Special instructions for users
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'method_type': self.method_type,
            'method_name': self.method_name,
            'is_active': self.is_active,
            'wallet_address': self.wallet_address,
            'usdt_wallet_address': self.usdt_wallet_address,
            'usdt_network': self.usdt_network,
            'account_name': self.account_name,
            'account_number': self.account_number,
            'bank_name': self.bank_name,
            'swift_code': self.swift_code,
            'email': self.email,
            'phone': self.phone,
            'qr_code': self.qr_code,
            'instructions': self.instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<PaymentMethod {self.method_name} ({self.method_type})>'
