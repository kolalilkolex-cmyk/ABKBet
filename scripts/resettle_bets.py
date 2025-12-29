"""
Re-settle bets with corrected selection values
"""
from app import create_app, db
from app.models import Bet, Match
import re

app = create_app()

with app.app_context():
    # Get all settled bets
    bets = Bet.query.filter(Bet.status.in_(['won', 'lost'])).all()
    
    print(f"Found {len(bets)} settled bets to re-check")
    
    corrected = 0
    for bet in bets:
        if not bet.match_id:
            continue
            
        match = bet.match
        if not match or match.home_score is None or match.away_score is None:
            continue
        
        desc = bet.event_description
        desc_lower = desc.lower()
        market = bet.market_type or ''
        selection = bet.selection or ''
        
        is_won = False
        bet_matched = False
        
        # Match Result (1X2)
        if '[Match Result]' in desc or 'match result' in desc_lower or '1x2' in market.lower():
            bet_matched = True
            selection_lower = selection.strip().lower()
            
            if match.home_score > match.away_score and selection_lower == 'home':
                is_won = True
            elif match.away_score > match.home_score and selection_lower == 'away':
                is_won = True
            elif match.home_score == match.away_score and selection_lower == 'draw':
                is_won = True
        
        # Over/Under
        elif 'over/under' in desc_lower or market.lower() in ['ou1', 'ou2', 'ou3']:
            bet_matched = True
            total_goals = match.home_score + match.away_score
            
            sel_lower = selection.lower()
            if sel_lower in ['over1', 'over 1.5']:
                is_won = total_goals > 1.5
            elif sel_lower in ['under1', 'under 1.5']:
                is_won = total_goals < 1.5
            elif sel_lower in ['over2', 'over 2.5']:
                is_won = total_goals > 2.5
            elif sel_lower in ['under2', 'under 2.5']:
                is_won = total_goals < 2.5
            elif sel_lower in ['over3', 'over 3.5']:
                is_won = total_goals > 3.5
            elif sel_lower in ['under3', 'under 3.5']:
                is_won = total_goals < 3.5
        
        # Both Teams to Score (BTTS/GG)
        elif 'both teams score' in desc_lower or 'gg' in market.lower():
            bet_matched = True
            both_scored = match.home_score > 0 and match.away_score > 0
            sel_lower = selection.lower()
            
            if sel_lower in ['yes', 'gg']:
                is_won = both_scored
            elif sel_lower in ['no', 'ng']:
                is_won = not both_scored
        
        # Correct Score
        elif 'correct score' in desc_lower or 'cs' in market.lower():
            bet_matched = True
            predicted_score = selection.strip()
            actual_score = f"{match.home_score}-{match.away_score}"
            is_won = predicted_score == actual_score
        
        if bet_matched:
            new_status = 'won' if is_won else 'lost'
            if bet.status != new_status:
                old_status = bet.status
                bet.status = new_status
                corrected += 1
                print(f"✓ Bet {bet.id}: {old_status.upper()} → {new_status.upper()} | {match.home_team} {match.home_score}-{match.away_score} {match.away_team} | Selected: {selection}")
    
    if corrected > 0:
        db.session.commit()
        print(f"\n✓ Corrected {corrected} bets")
    else:
        print("\nAll bets are correctly settled")
