"""
Add sample matches for testing on PythonAnywhere
Run this on PythonAnywhere with: python add_sample_matches.py
"""
from app import create_app, db
from app.models import Match
from datetime import datetime, timedelta

def add_sample_matches():
    app = create_app('production')
    
    with app.app_context():
        # Check if matches already exist
        existing = Match.query.count()
        if existing > 0:
            print(f'✓ {existing} matches already exist')
            return
        
        # Create sample matches
        now = datetime.utcnow()
        
        matches = [
            Match(
                league='English Premier League',
                home_team='Manchester United',
                away_team='Liverpool',
                match_date=now + timedelta(days=2, hours=3),
                home_odds=2.10,
                draw_odds=3.40,
                away_odds=3.20,
                status='scheduled'
            ),
            Match(
                league='Spanish La Liga',
                home_team='Real Madrid',
                away_team='Barcelona',
                match_date=now + timedelta(days=3, hours=5),
                home_odds=2.25,
                draw_odds=3.30,
                away_odds=3.00,
                status='scheduled'
            ),
            Match(
                league='German Bundesliga',
                home_team='Bayern Munich',
                away_team='Borussia Dortmund',
                match_date=now + timedelta(days=4, hours=2),
                home_odds=1.85,
                draw_odds=3.60,
                away_odds=4.20,
                status='scheduled'
            ),
            Match(
                league='Italian Serie A',
                home_team='Juventus',
                away_team='AC Milan',
                match_date=now + timedelta(days=5, hours=4),
                home_odds=2.40,
                draw_odds=3.20,
                away_odds=2.90,
                status='scheduled'
            ),
            Match(
                league='French Ligue 1',
                home_team='Paris Saint-Germain',
                away_team='Marseille',
                match_date=now + timedelta(days=6, hours=3),
                home_odds=1.65,
                draw_odds=3.80,
                away_odds=5.50,
                status='scheduled'
            )
        ]
        
        for match in matches:
            db.session.add(match)
        
        db.session.commit()
        
        print(f'✓ Successfully added {len(matches)} sample matches')
        print('\nMatches added:')
        for match in matches:
            print(f'  • {match.home_team} vs {match.away_team} ({match.league})')
            print(f'    Date: {match.match_date.strftime("%Y-%m-%d %H:%M UTC")}')
            print(f'    Odds: {match.home_odds} / {match.draw_odds} / {match.away_odds}')

if __name__ == '__main__':
    add_sample_matches()
