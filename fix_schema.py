import sqlite3
conn = sqlite3.connect(r"C:\Users\HP\Documents\ABKBet\betting.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bets'")
if cursor.fetchone():
    print("Bets table exists")
    try:
        cursor.execute("ALTER TABLE bets ADD COLUMN market_type VARCHAR(50)")
        print("Added market_type")
    except Exception as e:
        print(f"market_type: {e}")
    try:
        cursor.execute("ALTER TABLE bets ADD COLUMN selection VARCHAR(100)")
        print("Added selection")
    except Exception as e:
        print(f"selection: {e}")
    conn.commit()
else:
    print("No bets table")
conn.close()
