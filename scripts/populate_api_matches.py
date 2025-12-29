"""
Script to populate database with matches from API-Football
Run this manually to fetch upcoming matches
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.services.football_api_service import football_api
from config import Config

def main():
    """Fetch and populate matches from API-Football"""
    
    print("=" * 60)
    print("API-Football Match Population Script")
    print("=" * 60)
    
    # Check if API is enabled
    if not Config.FOOTBALL_API_ENABLED:
        print("❌ Football API is not enabled")
        print("Set FOOTBALL_API_ENABLED=true in your environment")
        return
    
    # Check if API key is configured
    if not Config.FOOTBALL_API_KEY:
        print("❌ Football API key is not configured")
        print("\nTo configure:")
        print("1. Sign up at https://www.api-football.com/")
        print("2. Get your API key from the dashboard")
        print("3. Set environment variable:")
        print("   Windows: $env:FOOTBALL_API_KEY='your_key_here'")
        print("   Linux/Mac: export FOOTBALL_API_KEY='your_key_here'")
        print("\n4. Enable the API:")
        print("   Windows: $env:FOOTBALL_API_ENABLED='true'")
        print("   Linux/Mac: export FOOTBALL_API_ENABLED='true'")
        return
    
    print(f"✓ API Key configured: {Config.FOOTBALL_API_KEY[:10]}...")
    print(f"✓ API Enabled: {Config.FOOTBALL_API_ENABLED}")
    print()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Initialize football API service
        football_api.initialize(Config.FOOTBALL_API_KEY)
        
        # Get popular leagues
        popular_leagues = football_api.get_popular_leagues()
        league_ids = [
            popular_leagues['premier_league'],
            popular_leagues['la_liga'],
            popular_leagues['bundesliga'],
            popular_leagues['serie_a'],
            popular_leagues['ligue_1'],
            popular_leagues['champions_league']
        ]
        
        print("Fetching upcoming matches from major leagues...")
        print("Leagues: Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League")
        matches = football_api.get_upcoming_matches(days=7, league_ids=league_ids)
        
        if not matches:
            print("❌ No matches found or API request failed")
            print("Check your API key and internet connection")
            return
        
        print(f"✓ Found {len(matches)} matches from API")
        print()
        
        # Sync to database
        print("Syncing matches to database...")
        created, updated = football_api.sync_matches_to_database(matches)
        
        print()
        print("=" * 60)
        print("Results:")
        print(f"  • New matches created: {created}")
        print(f"  • Existing matches updated: {updated}")
        print(f"  • Total processed: {created + updated}")
        print("=" * 60)
        print()
        
        if created + updated > 0:
            print("✓ Success! Matches are now available on your site")
            print("  Visit http://localhost:5000 to see them")
        else:
            print("⚠ No matches were synced")
            print("  This might be normal if all matches were already in the database")
        
        print()
        print("Note: Odds will be populated from API data")
        print("Run update_odds_loop.py to keep odds updated in real-time")


if __name__ == '__main__':
    main()
