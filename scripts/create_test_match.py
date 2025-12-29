"""
Create a test match for manual betting
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Match, MatchStatus

def create_test_matches():
    """Create some test matches"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Create a few test matches
            matches = [
                {
                    'home_team': 'Manchester United',
                    'away_team': 'Liverpool',
                    'league': 'Premier League',
                    'match_date': datetime.utcnow() + timedelta(hours=2),
                    'home_odds': 2.10,
                    'draw_odds': 3.40,
                    'away_odds': 3.20,
                    'status': MatchStatus.SCHEDULED.value,
                    'is_manual': True
                },
                {
                    'home_team': 'Real Madrid',
                    'away_team': 'Barcelona',
                    'league': 'La Liga',
                    'match_date': datetime.utcnow() + timedelta(hours=4),
                    'home_odds': 2.25,
                    'draw_odds': 3.10,
                    'away_odds': 3.00,
                    'status': MatchStatus.SCHEDULED.value,
                    'is_manual': True
                },
                {
                    'home_team': 'Bayern Munich',
                    'away_team': 'Borussia Dortmund',
                    'league': 'Bundesliga',
                    'match_date': datetime.utcnow() + timedelta(hours=6),
                    'home_odds': 1.75,
                    'draw_odds': 3.80,
                    'away_odds': 4.50,
                    'status': MatchStatus.SCHEDULED.value,
                    'is_manual': True
                }
            ]
            
            created_count = 0
            for match_data in matches:
                match = Match(**match_data)
                db.session.add(match)
                created_count += 1
            
            db.session.commit()
            
            print(f"✅ Created {created_count} test matches successfully!")
            print("\nMatches created:")
            for i, match_data in enumerate(matches, 1):
                print(f"  {i}. {match_data['home_team']} vs {match_data['away_team']}")
                print(f"     League: {match_data['league']}")
                print(f"     Odds: {match_data['home_odds']} / {match_data['draw_odds']} / {match_data['away_odds']}")
                print()
            
        except Exception as e:
            print(f"❌ Error creating matches: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("Creating test matches...")
    success = create_test_matches()
    sys.exit(0 if success else 1)
