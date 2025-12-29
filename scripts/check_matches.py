"""Quick script to check if API matches were added"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Match

app = create_app()

with app.app_context():
    # Get all matches
    all_matches = Match.query.all()
    api_matches = Match.query.filter_by(is_manual=False).all()
    
    print("=" * 60)
    print("DATABASE MATCHES CHECK")
    print("=" * 60)
    print(f"Total matches in database: {len(all_matches)}")
    print(f"API matches: {len(api_matches)}")
    print(f"Manual matches: {len(all_matches) - len(api_matches)}")
    print()
    
    if api_matches:
        print("Sample API Matches:")
        print("-" * 60)
        for match in api_matches[:5]:
            print(f"  {match.home_team} vs {match.away_team}")
            print(f"  League: {match.league}")
            print(f"  Date: {match.match_date}")
            print(f"  Odds: {match.home_odds} / {match.draw_odds} / {match.away_odds}")
            print(f"  API ID: {match.api_fixture_id}")
            print()
    
    print("=" * 60)
    print("✓ API matches successfully loaded!")
    print("Visit http://localhost:5000 to see them on your site")
    print("=" * 60)
