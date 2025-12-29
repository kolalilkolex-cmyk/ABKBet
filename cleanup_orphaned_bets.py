"""
Cleanup Orphaned Bets Script
Finds and removes bets that reference deleted users or are otherwise corrupted
"""
import sqlite3
import sys
from datetime import datetime

# Database path
DB_PATH = 'instance/betting.db'

def connect_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def find_orphaned_bets(conn):
    """Find bets with deleted users"""
    cursor = conn.cursor()
    
    # Find bets where user doesn't exist
    cursor.execute("""
        SELECT b.* 
        FROM bets b
        LEFT JOIN users u ON b.user_id = u.id
        WHERE u.id IS NULL
    """)
    
    orphaned = cursor.fetchall()
    return orphaned

def find_bets_by_match(conn, match_id):
    """Find all bets for a specific match"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, b.user_id, b.match_id, b.amount, b.status, b.created_at,
               u.username
        FROM bets b
        LEFT JOIN users u ON b.user_id = u.id
        WHERE b.match_id = ?
    """, (match_id,))
    
    return cursor.fetchall()

def get_all_matches(conn):
    """Get all manual matches"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, home_team, away_team, league, status
        FROM matches
        WHERE is_manual = 1
        ORDER BY id DESC
    """)
    
    return cursor.fetchall()

def delete_bet(conn, bet_id):
    """Delete a specific bet"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bets WHERE id = ?", (bet_id,))
    conn.commit()
    print(f"  ✓ Deleted bet #{bet_id}")

def main():
    print("=" * 70)
    print("ABKBet - Orphaned Bets Cleanup Tool")
    print("=" * 70)
    print()
    
    conn = connect_db()
    
    # 1. Find orphaned bets (deleted users)
    print("1. Checking for bets with deleted users...")
    orphaned = find_orphaned_bets(conn)
    
    if orphaned:
        print(f"   Found {len(orphaned)} orphaned bets:")
        for bet in orphaned:
            print(f"   - Bet #{bet['id']}: User #{bet['user_id']} (DELETED), "
                  f"Amount: ${bet['amount']:.2f}, Status: {bet['status']}")
        
        print()
        delete_orphaned = input("Delete these orphaned bets? (yes/no): ").strip().lower()
        
        if delete_orphaned == 'yes':
            for bet in orphaned:
                delete_bet(conn, bet['id'])
            print(f"✓ Deleted {len(orphaned)} orphaned bets")
        else:
            print("Skipped orphaned bets deletion")
    else:
        print("   ✓ No orphaned bets found")
    
    print()
    
    # 2. Check manual matches with bets
    print("2. Checking manual matches with bets...")
    matches = get_all_matches(conn)
    
    matches_with_bets = []
    for match in matches:
        bets = find_bets_by_match(conn, match['id'])
        if bets:
            matches_with_bets.append((match, bets))
    
    if matches_with_bets:
        print(f"   Found {len(matches_with_bets)} manual matches with bets:")
        print()
        
        for match, bets in matches_with_bets:
            print(f"   Match #{match['id']}: {match['home_team']} vs {match['away_team']}")
            print(f"   League: {match['league']}, Status: {match['status']}")
            print(f"   Bets ({len(bets)}):")
            
            for bet in bets:
                username = bet['username'] if bet['username'] else f"[DELETED USER #{bet['user_id']}]"
                print(f"     - Bet #{bet['id']}: {username}, "
                      f"${bet['amount']:.2f}, Status: {bet['status']}")
            
            print()
            action = input(f"   Delete bets for Match #{match['id']}? (yes/no/skip): ").strip().lower()
            
            if action == 'yes':
                for bet in bets:
                    delete_bet(conn, bet['id'])
                print(f"   ✓ Deleted {len(bets)} bet(s) for Match #{match['id']}")
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
    
    conn.close()

if __name__ == '__main__':
    main()
