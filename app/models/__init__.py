from app.extensions import db
from datetime import datetime
from enum import Enum

# Import DepositRequest model
from app.models.deposit import DepositRequest

class BetStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"
    VOIDED = "voided"

class TransactionStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=0.0)  # USD balance
    is_admin = db.Column(db.Boolean, default=False)  # Admin flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(255), nullable=True)  # Password reset token
    reset_token_expiry = db.Column(db.DateTime, nullable=True)  # Token expiration time
    
    # Payment/Withdrawal Details
    withdrawal_wallet = db.Column(db.String(255), nullable=True)  # User's withdrawal address
    bank_account_name = db.Column(db.String(255), nullable=True)  # Bank account holder name
    bank_account_number = db.Column(db.String(100), nullable=True)  # Bank account number
    bank_name = db.Column(db.String(255), nullable=True)  # Bank name
    paypal_email = db.Column(db.String(255), nullable=True)  # PayPal email
    skrill_email = db.Column(db.String(255), nullable=True)  # Skrill email
    usdt_wallet = db.Column(db.String(255), nullable=True)  # USDT wallet address
    payment_notes = db.Column(db.Text, nullable=True)  # Additional payment info/notes
    
    # Relationships
    wallet = db.relationship('Wallet', uselist=False, back_populates='user', cascade='all, delete-orphan')
    bets = db.relationship('Bet', back_populates='user', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    bitcoin_address = db.Column(db.String(255), unique=True, nullable=False)
    private_key_encrypted = db.Column(db.String(255), nullable=True)
    total_received = db.Column(db.Float, default=0.0)  # in BTC
    total_sent = db.Column(db.Float, default=0.0)      # in BTC
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='wallet')
    
    def __repr__(self):
        return f'<Wallet {self.bitcoin_address}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tx_hash = db.Column(db.String(255), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)  # in BTC
    transaction_type = db.Column(db.String(20), nullable=False)  # 'deposit' or 'withdrawal'
    status = db.Column(db.String(20), default=TransactionStatus.PENDING.value)
    confirmations = db.Column(db.Integer, default=0)
    from_address = db.Column(db.String(255), nullable=True)
    to_address = db.Column(db.String(255), nullable=True)
    fee = db.Column(db.Float, default=0.0)  # in BTC
    payment_method = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', back_populates='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.tx_hash[:8]}...>'

class MatchStatus(Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    league = db.Column(db.String(100), nullable=True)
    match_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default=MatchStatus.SCHEDULED.value)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    match_time = db.Column(db.Integer, nullable=True)  # Elapsed minutes for live matches (1-90+)
    
    # Half-time scores
    ht_home_score = db.Column(db.Integer, nullable=True)
    ht_away_score = db.Column(db.Integer, nullable=True)
    ht_status = db.Column(db.String(20), default='pending')  # pending, completed
    
    # 1X2 Odds (Match Result)
    home_odds = db.Column(db.Float, nullable=False, default=2.0)
    draw_odds = db.Column(db.Float, nullable=False, default=3.0)
    away_odds = db.Column(db.Float, nullable=False, default=2.5)
    
    # Double Chance Odds
    home_draw_odds = db.Column(db.Float, nullable=True)  # 1X
    home_away_odds = db.Column(db.Float, nullable=True)  # 12
    draw_away_odds = db.Column(db.Float, nullable=True)  # X2
    
    # Both Teams to Score (GG/NG)
    gg_odds = db.Column(db.Float, nullable=True)  # Both teams score
    ng_odds = db.Column(db.Float, nullable=True)  # No goal / One team doesn't score
    
    # Over/Under 2.5 Goals
    over25_odds = db.Column(db.Float, nullable=True)
    under25_odds = db.Column(db.Float, nullable=True)
    
    # Over/Under 1.5 Goals
    over15_odds = db.Column(db.Float, nullable=True)
    under15_odds = db.Column(db.Float, nullable=True)
    
    # Over/Under 3.5 Goals
    over35_odds = db.Column(db.Float, nullable=True)
    under35_odds = db.Column(db.Float, nullable=True)
    
    # Half Time/Full Time (HT/FT) - stored as JSON
    htft_odds = db.Column(db.Text, nullable=True)  # JSON string of HT/FT odds
    
    # Correct Score - stored as JSON
    correct_score_odds = db.Column(db.Text, nullable=True)  # JSON string of score odds
    
    is_manual = db.Column(db.Boolean, default=True)  # True for manually managed matches
    api_fixture_id = db.Column(db.Integer, nullable=True)  # For API-based matches
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Match {self.home_team} vs {self.away_team}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'league': self.league,
            'match_date': self.match_date.isoformat() if self.match_date else None,
            'status': self.status,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'match_time': self.match_time,  # Add match time in minutes
            'ht_home_score': self.ht_home_score,
            'ht_away_score': self.ht_away_score,
            'ht_status': self.ht_status,
            'home_odds': self.home_odds,
            'draw_odds': self.draw_odds,
            'away_odds': self.away_odds,
            'home_draw_odds': self.home_draw_odds,
            'home_away_odds': self.home_away_odds,
            'draw_away_odds': self.draw_away_odds,
            'gg_odds': self.gg_odds,
            'ng_odds': self.ng_odds,
            'over25_odds': self.over25_odds,
            'under25_odds': self.under25_odds,
            'over15_odds': self.over15_odds,
            'under15_odds': self.under15_odds,
            'over35_odds': self.over35_odds,
            'under35_odds': self.under35_odds,
            'htft_odds': self.htft_odds,
            'correct_score_odds': self.correct_score_odds,
            'is_manual': self.is_manual
        }

class Bet(db.Model):
    __tablename__ = 'bets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=True)  # Link to match
    amount = db.Column(db.Float, nullable=False)  # in BTC
    odds = db.Column(db.Float, nullable=False)
    potential_payout = db.Column(db.Float, nullable=False)  # amount * odds
    bet_type = db.Column(db.String(50), nullable=False)  # e.g., 'sports', 'esports', 'crypto'
    market_type = db.Column(db.String(50), nullable=True)  # e.g., '1x2', 'gg', 'ou2', 'cs'
    selection = db.Column(db.String(100), nullable=True)   # selected option label (e.g., 'home', '2-1')
    event_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=BetStatus.PENDING.value)
    result = db.Column(db.String(20), nullable=True)  # 'win' or 'loss'
    settled_payout = db.Column(db.Float, nullable=True)  # actual payout amount
    booking_code = db.Column(db.String(10), nullable=True)  # Associated booking code
    cashout_value = db.Column(db.Float, nullable=True)  # Current cashout value
    is_cashed_out = db.Column(db.Boolean, default=False)  # Whether bet was cashed out
    cashed_out_at = db.Column(db.DateTime, nullable=True)  # When bet was cashed out
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    settled_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='bets')
    match = db.relationship('Match', backref='bets', foreign_keys=[match_id])
    
    def __repr__(self):
        return f'<Bet {self.id} - {self.status}>'

class BookingCode(db.Model):
    __tablename__ = 'booking_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    bet_data = db.Column(db.Text, nullable=False)  # JSON string of bet selections
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_count = db.Column(db.Integer, default=0)
    
    # Relationship
    user = db.relationship('User', backref='booking_codes')
    
    def __repr__(self):
        return f'<BookingCode {self.code}>'
