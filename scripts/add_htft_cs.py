"""
Add HT/FT and Correct Score columns to matches table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN htft_odds TEXT"))
            print("✓ Added htft_odds column")
        except Exception as e:
            print(f"htft_odds: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN correct_score_odds TEXT"))
            print("✓ Added correct_score_odds column")
        except Exception as e:
            print(f"correct_score_odds: {e}")
        
        conn.commit()
    
    print("\n✅ Database migration completed!")
    print("HT/FT and Correct Score columns added to matches table")
