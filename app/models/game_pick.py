"""
Game Pick (Match) Model - Stores football match data and odds
"""
from app import db
from datetime import datetime


class GamePick(db.Model):
    """Model for storing football matches and their betting odds"""
    __tablename__ = 'game_picks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Match Information
    match_name = db.Column(db.String(200), nullable=False)
    league = db.Column(db.String(100), nullable=False)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    kick_off_time = db.Column(db.DateTime, nullable=False)
    
    # API Integration Fields
    api_fixture_id = db.Column(db.Integer, unique=True, nullable=True)  # API-Football fixture ID
    api_league_id = db.Column(db.Integer, nullable=True)  # API-Football league ID
    
    # Live Match Data
    status = db.Column(db.String(20), default='NS')  # NS=Not Started, 1H=First Half, HT=Half Time, 2H=Second Half, FT=Finished
    elapsed_time = db.Column(db.Integer, nullable=True)  # Minutes elapsed
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    
    # Match Winner (1X2) Odds
    odds_home = db.Column(db.Float, default=2.0)
    odds_draw = db.Column(db.Float, default=3.0)
    odds_away = db.Column(db.Float, default=2.0)
    
    # Over/Under Goals Odds
    odds_over_1_5 = db.Column(db.Float, default=1.5)
    odds_under_1_5 = db.Column(db.Float, default=2.5)
    odds_over_2_5 = db.Column(db.Float, default=1.8)
    odds_under_2_5 = db.Column(db.Float, default=2.0)
    odds_over_3_5 = db.Column(db.Float, default=2.5)
    odds_under_3_5 = db.Column(db.Float, default=1.5)
    
    # Both Teams to Score Odds
    odds_btts_yes = db.Column(db.Float, default=1.8)
    odds_btts_no = db.Column(db.Float, default=2.0)
    
    # Double Chance Odds
    odds_home_or_draw = db.Column(db.Float, default=1.3)
    odds_away_or_draw = db.Column(db.Float, default=1.3)
    odds_home_or_away = db.Column(db.Float, default=1.4)
    
    # Correct Score Odds (popular scores)
    odds_1_0 = db.Column(db.Float, default=7.0)
    odds_2_0 = db.Column(db.Float, default=9.0)
    odds_2_1 = db.Column(db.Float, default=9.0)
    odds_3_0 = db.Column(db.Float, default=15.0)
    odds_0_0 = db.Column(db.Float, default=10.0)
    odds_1_1 = db.Column(db.Float, default=6.0)
    odds_2_2 = db.Column(db.Float, default=15.0)
    odds_0_1 = db.Column(db.Float, default=8.0)
    odds_0_2 = db.Column(db.Float, default=11.0)
    odds_1_2 = db.Column(db.Float, default=10.0)
    
    # Half-Time/Full-Time Odds
    odds_ht_ft_home_home = db.Column(db.Float, default=3.5)
    odds_ht_ft_draw_home = db.Column(db.Float, default=5.0)
    odds_ht_ft_away_home = db.Column(db.Float, default=10.0)
    odds_ht_ft_home_draw = db.Column(db.Float, default=8.0)
    odds_ht_ft_draw_draw = db.Column(db.Float, default=4.5)
    odds_ht_ft_away_draw = db.Column(db.Float, default=8.0)
    odds_ht_ft_home_away = db.Column(db.Float, default=12.0)
    odds_ht_ft_draw_away = db.Column(db.Float, default=5.5)
    odds_ht_ft_away_away = db.Column(db.Float, default=4.0)
    
    # Metadata
    settled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GamePick {self.match_name}>'
    
    def to_dict(self):
        """Convert match to dictionary for API responses"""
        return {
            'id': self.id,
            'match_name': self.match_name,
            'league': self.league,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'kick_off_time': self.kick_off_time.isoformat() if self.kick_off_time else None,
            'status': self.status,
            'elapsed_time': self.elapsed_time,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'odds': {
                'match_winner': {
                    'home': self.odds_home,
                    'draw': self.odds_draw,
                    'away': self.odds_away
                },
                'over_under': {
                    'over_1_5': self.odds_over_1_5,
                    'under_1_5': self.odds_under_1_5,
                    'over_2_5': self.odds_over_2_5,
                    'under_2_5': self.odds_under_2_5,
                    'over_3_5': self.odds_over_3_5,
                    'under_3_5': self.odds_under_3_5
                },
                'btts': {
                    'yes': self.odds_btts_yes,
                    'no': self.odds_btts_no
                },
                'double_chance': {
                    'home_or_draw': self.odds_home_or_draw,
                    'away_or_draw': self.odds_away_or_draw,
                    'home_or_away': self.odds_home_or_away
                },
                'correct_score': {
                    '1-0': self.odds_1_0,
                    '2-0': self.odds_2_0,
                    '2-1': self.odds_2_1,
                    '3-0': self.odds_3_0,
                    '0-0': self.odds_0_0,
                    '1-1': self.odds_1_1,
                    '2-2': self.odds_2_2,
                    '0-1': self.odds_0_1,
                    '0-2': self.odds_0_2,
                    '1-2': self.odds_1_2
                },
                'ht_ft': {
                    'home_home': self.odds_ht_ft_home_home,
                    'draw_home': self.odds_ht_ft_draw_home,
                    'away_home': self.odds_ht_ft_away_home,
                    'home_draw': self.odds_ht_ft_home_draw,
                    'draw_draw': self.odds_ht_ft_draw_draw,
                    'away_draw': self.odds_ht_ft_away_draw,
                    'home_away': self.odds_ht_ft_home_away,
                    'draw_away': self.odds_ht_ft_draw_away,
                    'away_away': self.odds_ht_ft_away_away
                }
            }
        }
