"""
Cleanup Orphaned Bets Script for PythonAnywhere
Finds and removes bets that reference deleted users or are otherwise corrupted
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, '/home/ABKBet/ABKBet')

from app import create_app
from app.models import db, Bet, User, Match

def find_orphaned_bets():
    """Find bets with deleted users"""
    # Query bets and check if user exists
    all_bets = Bet.query.all()
    orphaned = []
    
    for bet in all_bets:
        try:
            # Try to access user
            if bet.user is None:
                orphaned.append(bet)
        except:
            orphaned.append(bet)
    
    return orphaned

def find_bets_by_match(match_id):
    """Find all bets for a specific match"""
    bets = Bet.query.filter_by(match_id=match_id).all()
    results = []
    
    for bet in bets:
        try:
            username = bet.user.username if bet.user else f"[DELETED USER #{bet.user_id}]"
        except:
            username = f"[ERROR USER #{bet.user_id}]"
        
        results.append({
            'bet': bet,
            'username': username
        })
    
    return results

def get_manual_matches():
    """Get all manual matches"""
    matches = Match.query.filter_by(is_manual=True).order_by(Match.id.desc()).all()
    return matches

def delete_bet(bet_id):
    """Delete a specific bet"""
    bet = Bet.query.get(bet_id)
    if bet:
        db.session.delete(bet)
        db.session.commit()
        print(f"  ✓ Deleted bet #{bet_id}")
        return True
    return False

def main():
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("ABKBet - Orphaned Bets Cleanup Tool")
        print("=" * 70)
        print()
        
        # 1. Find orphaned bets (deleted users)
        print("1. Checking for bets with deleted users...")
        orphaned = find_orphaned_bets()
        
        if orphaned:
            print(f"   Found {len(orphaned)} orphaned bets:")
            for bet in orphaned:
                print(f"   - Bet #{bet.id}: User #{bet.user_id} (DELETED), "
                      f"Amount: ${bet.amount:.2f}, Status: {bet.status}")
            
            print()
            delete_orphaned = input("Delete these orphaned bets? (yes/no): ").strip().lower()
            
            if delete_orphaned == 'yes':
                for bet in orphaned:
                    delete_bet(bet.id)
                print(f"✓ Deleted {len(orphaned)} orphaned bets")
            else:
                print("Skipped orphaned bets deletion")
        else:
            print("   ✓ No orphaned bets found")
        
        print()
        
        # 2. Check manual matches with bets
        print("2. Checking manual matches with bets...")
        matches = get_manual_matches()
        
        matches_with_bets = []
        for match in matches:
            bets = find_bets_by_match(match.id)
            if bets:
                matches_with_bets.append((match, bets))
        
        if matches_with_bets:
            print(f"   Found {len(matches_with_bets)} manual matches with bets:")
            print()
            
            for match, bets in matches_with_bets:
                print(f"   Match #{match.id}: {match.home_team} vs {match.away_team}")
                print(f"   League: {match.league}, Status: {match.status}")
                print(f"   Bets ({len(bets)}):")
                
                for bet_info in bets:
                    bet = bet_info['bet']
                    username = bet_info['username']
                    print(f"     - Bet #{bet.id}: {username}, "
                          f"${bet.amount:.2f}, Status: {bet.status}")
                
                print()
                action = input(f"   Delete bets for Match #{match.id}? (yes/no/skip): ").strip().lower()
                
                if action == 'yes':
                    for bet_info in bets:
                        delete_bet(bet_info['bet'].id)
                    print(f"   ✓ Deleted {len(bets)} bet(s) for Match #{match.id}")
                    print()
                elif action == 'skip':
                    print("   Exiting...")
                    break
                else:
                    print("   Skipped")
                    print()
        else:
            print("   ✓ No manual matches with bets found")
        
        print()
        print("=" * 70)
        print("Cleanup Complete!")
        print("=" * 70)

if __name__ == '__main__':
    main()
