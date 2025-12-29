from app.extensions import db
from datetime import datetime
from enum import Enum

class VirtualGameStatus(Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class VirtualLeague(db.Model):
    __tablename__ = 'virtual_leagues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    game_duration_seconds = db.Column(db.Integer, default=180)  # Default 3 minutes per game
    games_per_day = db.Column(db.Integer, default=48)  # How many games per day
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teams = db.relationship('VirtualTeam', back_populates='league', cascade='all, delete-orphan')
    games = db.relationship('VirtualGame', back_populates='league', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VirtualLeague {self.name}>'
    
    def to_dict(self):
        from sqlalchemy import func
        teams_count = db.session.query(func.count(VirtualTeam.id)).filter_by(league_id=self.id).scalar() or 0
        games_count = db.session.query(func.count(VirtualGame.id)).filter_by(league_id=self.id).scalar() or 0
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'logo_url': self.logo_url,
            'is_active': self.is_active,
            'game_duration_seconds': self.game_duration_seconds,
            'games_per_day': self.games_per_day,
            'teams_count': teams_count,
            'games_count': games_count
        }

class VirtualTeam(db.Model):
    __tablename__ = 'virtual_teams'
    
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('virtual_leagues.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Integer, default=75)  # Team strength rating (0-100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    league = db.relationship('VirtualLeague', back_populates='teams')
    
    def __repr__(self):
        return f'<VirtualTeam {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'league_id': self.league_id,
            'name': self.name,
            'logo_url': self.logo_url,
            'rating': self.rating
        }

class VirtualGame(db.Model):
    __tablename__ = 'virtual_games'
    
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('virtual_leagues.id'), nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('virtual_teams.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('virtual_teams.id'), nullable=False)
    
    # Game timing
    scheduled_start = db.Column(db.DateTime, nullable=False)
    actual_start = db.Column(db.DateTime, nullable=True)
    game_duration = db.Column(db.Integer, default=180)  # Duration in seconds
    
    # Status
    status = db.Column(db.String(20), default=VirtualGameStatus.SCHEDULED.value)
    current_minute = db.Column(db.Integer, default=0)  # Virtual minute (0-90)
    
    # Scores
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    ht_home_score = db.Column(db.Integer, nullable=True)
    ht_away_score = db.Column(db.Integer, nullable=True)
    
    # Odds - 1X2
    home_odds = db.Column(db.Float, nullable=False, default=2.0)
    draw_odds = db.Column(db.Float, nullable=False, default=3.0)
    away_odds = db.Column(db.Float, nullable=False, default=2.5)
    
    # Double Chance
    home_draw_odds = db.Column(db.Float, nullable=True)
    home_away_odds = db.Column(db.Float, nullable=True)
    draw_away_odds = db.Column(db.Float, nullable=True)
    
    # Both Teams to Score
    gg_odds = db.Column(db.Float, nullable=True)
    ng_odds = db.Column(db.Float, nullable=True)
    
    # Over/Under
    over15_odds = db.Column(db.Float, nullable=True)
    under15_odds = db.Column(db.Float, nullable=True)
    over25_odds = db.Column(db.Float, nullable=True)
    under25_odds = db.Column(db.Float, nullable=True)
    over35_odds = db.Column(db.Float, nullable=True)
    under35_odds = db.Column(db.Float, nullable=True)
    
    # Correct Score - stored as JSON
    correct_score_odds = db.Column(db.Text, nullable=True)
    
    # Game events (JSON) - stores minute-by-minute events like goals, cards, etc.
    events = db.Column(db.Text, nullable=True)
    
    # Admin control
    is_auto_play = db.Column(db.Boolean, default=True)  # Auto-play or manual control
    result_set_manually = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    league = db.relationship('VirtualLeague', back_populates='games')
    home_team = db.relationship('VirtualTeam', foreign_keys=[home_team_id])
    away_team = db.relationship('VirtualTeam', foreign_keys=[away_team_id])
    
    def __repr__(self):
        return f'<VirtualGame {self.id}: {self.home_team.name if self.home_team else "?"} vs {self.away_team.name if self.away_team else "?"}>'
    
    def to_dict(self):
        # Get team names
        home_team_name = self.home_team.name if self.home_team else 'Unknown'
        away_team_name = self.away_team.name if self.away_team else 'Unknown'
        
        # Only include scores if game is in_progress or finished
        include_scores = self.status in ['in_progress', 'finished']
        
        result = {
            'id': self.id,
            'league_id': self.league_id,
            'league_name': self.league.name if self.league else None,
            'home_team': home_team_name,
            'away_team': away_team_name,
            'home_team_obj': self.home_team.to_dict() if self.home_team else None,
            'away_team_obj': self.away_team.to_dict() if self.away_team else None,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'scheduled_time': self.scheduled_start.isoformat() if self.scheduled_start else None,  # For compatibility
            'actual_start': self.actual_start.isoformat() if self.actual_start else None,
            'game_duration': self.game_duration,
            'status': self.status,
            'current_minute': self.current_minute if include_scores else 0,
            'home_score': self.home_score if include_scores else None,
            'away_score': self.away_score if include_scores else None,
            'ht_home_score': self.ht_home_score,
            'ht_away_score': self.ht_away_score,
            'home_odds': self.home_odds,
            'draw_odds': self.draw_odds,
            'away_odds': self.away_odds,
            'home_draw_odds': self.home_draw_odds,
            'home_away_odds': self.home_away_odds,
            'draw_away_odds': self.draw_away_odds,
            'gg_odds': self.gg_odds,
            'ng_odds': self.ng_odds,
            'over15_odds': self.over15_odds,
            'under15_odds': self.under15_odds,
            'over25_odds': self.over25_odds,
            'under25_odds': self.under25_odds,
            'over35_odds': self.over35_odds,
            'under35_odds': self.under35_odds,
            'correct_score_odds': self.correct_score_odds,
            'events': self.events,
            'is_auto_play': self.is_auto_play,
            'result_set_manually': self.result_set_manually,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            # Add odds object for frontend compatibility
            'odds': {
                'home_win': self.home_odds,
                'draw': self.draw_odds,
                'away_win': self.away_odds,
                'over_25': self.over25_odds,
                'under_25': self.under25_odds,
                'gg': self.gg_odds,
                'ng': self.ng_odds
            } if self.home_odds else None,
            # Add status_text for frontend - format scheduled time nicely
            'status_text': self.status.replace('_', ' ').title() if self.status else 'Scheduled'
        }
        
        return result
