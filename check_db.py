import sqlite3

conn = sqlite3.connect('instance/betting.db')
c = conn.cursor()

# Get all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()

print("=" * 60)
print("DATABASE CHECK")
print("=" * 60)
print("\nTables in database:")
for table in tables:
    print(f"  - {table[0]}")
    
# Check matches table
try:
    c.execute("SELECT COUNT(*) FROM matches")
    count = c.fetchone()[0]
    print(f"\nTotal matches: {count}")
    
    c.execute("SELECT COUNT(*) FROM matches WHERE is_manual = 0")
    api_count = c.fetchone()[0]
    print(f"API matches (is_manual=0): {api_count}")
    
    c.execute("SELECT COUNT(*) FROM matches WHERE is_manual = 1")
    manual_count = c.fetchone()[0]
    print(f"Manual matches (is_manual=1): {manual_count}")
    
    print("\nFirst 5 matches:")
    c.execute("SELECT id, home_team, away_team, is_manual, api_fixture_id FROM matches LIMIT 5")
    rows = c.fetchall()
    for row in rows:
        print(f"  {row[0]}: {row[1]} vs {row[2]} (manual={row[3]}, api_id={row[4]})")
        
except Exception as e:
    print(f"\nError checking matches: {e}")

print("=" * 60)
conn.close()
