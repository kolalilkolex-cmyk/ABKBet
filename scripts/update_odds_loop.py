"""
Background script to continuously update match odds from API-Football
Runs every 15 minutes to refresh odds for upcoming and live matches
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.services.football_api_service import football_api
from app.models import Match, MatchStatus
from config import Config

UPDATE_INTERVAL = 900  # 15 minutes in seconds


def update_all_odds(app):
    """Update odds for all scheduled and live matches"""
    
    with app.app_context():
        # Get all matches that need odds updates (scheduled or live)
        matches = Match.query.filter(
            Match.status.in_([MatchStatus.SCHEDULED.value, MatchStatus.LIVE.value]),
            Match.api_fixture_id.isnot(None)
        ).all()
        
        if not matches:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No matches need odds updates")
            return
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating odds for {len(matches)} matches...")
        
        success_count = 0
        fail_count = 0
        
        for match in matches:
            try:
                if football_api.update_match_odds(match.api_fixture_id, match.id):
                    success_count += 1
                else:
                    fail_count += 1
                
                # Small delay to avoid rate limiting
                time.sleep(1)
            
            except Exception as e:
                print(f"  Error updating match {match.id}: {e}")
                fail_count += 1
        
        print(f"  ✓ Updated: {success_count}, Failed: {fail_count}")


def sync_live_matches(app):
    """Sync live matches from API"""
    
    with app.app_context():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking for live matches...")
        
        live_matches = football_api.get_live_matches()
        
        if live_matches:
            created, updated = football_api.sync_matches_to_database(live_matches)
            if created + updated > 0:
                print(f"  ✓ Live matches: {created} new, {updated} updated")


def main():
    """Main loop to continuously update odds"""
    
    print("=" * 60)
    print("API-Football Odds Update Loop")
    print("Updates odds every 15 minutes")
    print("=" * 60)
    print()
    
    # Check if API is enabled
    if not Config.FOOTBALL_API_ENABLED:
        print("❌ Football API is not enabled")
        print("Set FOOTBALL_API_ENABLED=true in your environment")
        return
    
    # Check if API key is configured
    if not Config.FOOTBALL_API_KEY:
        print("❌ Football API key is not configured")
        return
    
    print(f"✓ API Key configured")
    print(f"✓ Update interval: {UPDATE_INTERVAL // 60} minutes")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Create Flask app context
    app = create_app()
    
    # Initialize football API service
    with app.app_context():
        football_api.initialize(Config.FOOTBALL_API_KEY)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n[Iteration {iteration}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            
            # Sync live matches
            sync_live_matches(app)
            
            # Update odds for scheduled and live matches
            update_all_odds(app)
            
            print(f"\n⏰ Next update in {UPDATE_INTERVAL // 60} minutes...")
            print("-" * 60)
            
            # Wait for next update
            time.sleep(UPDATE_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Stopping odds update loop...")
        print(f"Total iterations completed: {iteration}")
        print("=" * 60)


if __name__ == '__main__':
    main()
