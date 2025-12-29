"""Deposit request model for manual approval system"""
from app.extensions import db
from datetime import datetime

class DepositRequest(db.Model):
    __tablename__ = 'deposit_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # in USD
    payment_method = db.Column(db.String(50), nullable=False)  # 'bitcoin', 'bank_transfer', 'paypal', etc.
    transaction_reference = db.Column(db.String(255), nullable=False)  # Transaction ID/proof
    payment_proof = db.Column(db.Text, nullable=True)  # Screenshot URL or additional proof
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text, nullable=True)  # Admin's rejection reason or notes
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin who approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='deposit_requests')
    admin = db.relationship('User', foreign_keys=[approved_by])
    
    def __repr__(self):
        return f'<DepositRequest {self.id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_reference': self.transaction_reference,
            'payment_proof': self.payment_proof,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'approved_by': self.approved_by,
            'admin_username': self.admin.username if self.admin else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
