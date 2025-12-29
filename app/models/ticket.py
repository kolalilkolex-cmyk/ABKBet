from datetime import datetime
from app.models import db

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_odds = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    picks = db.relationship('GamePick', backref='ticket', lazy=True)

class GamePick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    match = db.Column(db.String(100), nullable=False)
    pick = db.Column(db.String(100), nullable=False)
    odds = db.Column(db.Float, nullable=False)