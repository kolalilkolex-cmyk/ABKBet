"""Update API matches from 'finished' to 'scheduled' status so they can be bet on"""
import sqlite3

conn = sqlite3.connect('instance/betting.db')
c = conn.cursor()

# Check current status
c.execute("SELECT COUNT(*) FROM matches WHERE is_manual=0 AND status='finished'")
finished_count = c.fetchone()[0]
print(f"API matches with 'finished' status: {finished_count}")

# Update to scheduled
c.execute("UPDATE matches SET status='scheduled' WHERE is_manual=0 AND status='finished'")
updated = c.rowcount
conn.commit()

print(f"Updated {updated} matches from 'finished' to 'scheduled'")

# Verify
c.execute("SELECT status, COUNT(*) FROM matches GROUP BY status")
print("\nCurrent status distribution:")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]} matches")

conn.close()
print("\n✓ Done! API matches are now available for betting")
