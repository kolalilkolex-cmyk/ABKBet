"""
Fix selection values for existing bets by parsing from event descriptions
"""
from app import create_app, db
from app.models import Bet
import re

app = create_app()

with app.app_context():
    # Get all single bets with wrong selection values
    bets = Bet.query.filter(Bet.selection.like('% picks')).all()
    
    print(f"Found {len(bets)} bets with '% picks' selection")
    
    updated = 0
    for bet in bets:
        # Skip multi-bets
        if 'MULTI:' in bet.event_description:
            continue
            
        desc = bet.event_description
        
        # Extract selection from description
        # Format: "PSG vs Medellin [Match Result] home @1.30"
        # or: "PSG vs Medellin - [Match Result] HOME @ 2.00"
        
        # Try to extract the part after ] and before @
        pattern = r'\]\s*([^\s@]+)\s*@'
        match = re.search(pattern, desc)
        
        if match:
            selection = match.group(1).strip().lower()
            # Remove any trailing punctuation
            selection = re.sub(r'[^\w-]', '', selection)
            
            if selection:
                old_selection = bet.selection
                bet.selection = selection
                updated += 1
                print(f"✓ Bet {bet.id}: '{old_selection}' → '{selection}' ({desc[:60]}...)")
        else:
            print(f"✗ Bet {bet.id}: Could not extract selection from: {desc[:80]}")
    
    if updated > 0:
        db.session.commit()
        print(f"\n✓ Updated {updated} bets")
    else:
        print("\nNo bets updated")
