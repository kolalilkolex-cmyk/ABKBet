from app.extensions import db
from datetime import datetime
from enum import Enum
import secrets

class PremiumBookingStatus(Enum):
    ACTIVE = "active"
    PURCHASED = "purchased"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class PremiumBooking(db.Model):
    """Premium booking codes created by admin that require payment to view"""
    __tablename__ = 'premium_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Match selections (stored as JSON)
    selections = db.Column(db.JSON, nullable=False)  # Array of {match_id, market, selection, odds}
    total_odds = db.Column(db.Float, nullable=False)
    
    # Pricing
    price_usd = db.Column(db.Float, default=250.0)
    
    # Admin info
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='active', nullable=False)
    
    # Metadata
    description = db.Column(db.String(500), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    purchases = db.relationship('PremiumBookingPurchase', back_populates='booking', cascade='all, delete-orphan')
    admin = db.relationship('User', foreign_keys=[created_by_admin_id])
    
    @staticmethod
    def generate_code():
        """Generate a unique 10-character booking code"""
        while True:
            code = 'PRM' + secrets.token_hex(4).upper()[:7]
            if not PremiumBooking.query.filter_by(booking_code=code).first():
                return code
    
    def to_dict(self, include_selections=False):
        """Convert to dictionary, optionally hiding selections"""
        data = {
            'id': self.id,
            'booking_code': self.booking_code,
            'total_odds': self.total_odds,
            'price_usd': self.price_usd,
            'status': self.status,
            'description': self.description,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat(),
            'num_selections': len(self.selections) if self.selections else 0
        }
        
        if include_selections:
            # Full access - show everything
            data['selections'] = self.selections
        else:
            # Preview mode - show only match names, hide selections/odds
            if self.selections:
                data['matches_preview'] = [
                    {
                        'match': sel.get('match', 'Unknown Match'),
                        'market': sel.get('market', 'Unknown Market')
                    }
                    for sel in self.selections
                ]
        
        return data
    
    def __repr__(self):
        return f'<PremiumBooking {self.booking_code}>'


class PremiumBookingPurchase(db.Model):
    """Tracks users who have purchased premium booking codes"""
    __tablename__ = 'premium_booking_purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('premium_bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Payment info
    amount_paid_usd = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='balance')  # balance, deposit, etc.
    
    # Timestamps
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('PremiumBooking', back_populates='purchases')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<PremiumBookingPurchase {self.booking_id} by User {self.user_id}>'
