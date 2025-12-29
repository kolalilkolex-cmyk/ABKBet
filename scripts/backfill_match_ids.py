"""
Backfill match_id for existing bets
"""
from app import create_app, db
from app.models import Bet, Match
import re

app = create_app()

with app.app_context():
    # Get all bets without match_id
    bets = Bet.query.filter(Bet.match_id.is_(None)).all()
    
    print(f"Found {len(bets)} bets without match_id")
    
    updated = 0
    for bet in bets:
        desc = bet.event_description
        
        # Skip multi-bets
        if 'MULTI:' in desc:
            continue
        
        # Extract match name
        match_name = None
        if ' vs ' in desc:
            # Try format with " - [" first
            if ' - [' in desc:
                match_name = desc.split(' - [')[0].strip()
            # Try format with " [" (no dash)
            elif ' [' in desc:
                match_name = desc.split(' [')[0].strip()
            
            if match_name:
                teams = match_name.split(' vs ')
                if len(teams) == 2:
                    home_team, away_team = teams[0].strip(), teams[1].strip()
                    
                    # Find match in database
                    match = Match.query.filter(
                        Match.home_team == home_team,
                        Match.away_team == away_team
                    ).first()
                    
                    if match:
                        bet.match_id = match.id
                        updated += 1
                        print(f"✓ Bet {bet.id}: Linked to match {match.id} ({match.home_team} vs {match.away_team})")
                    else:
                        print(f"✗ Bet {bet.id}: No match found for {home_team} vs {away_team}")
    
    if updated > 0:
        db.session.commit()
        print(f"\n✓ Updated {updated} bets")
    else:
        print("\nNo bets updated")
