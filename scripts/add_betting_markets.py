"""
Add additional betting market columns to matches table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

with app.app_context():
    # Add new columns using raw SQL
    with db.engine.connect() as conn:
        try:
            # Double Chance odds
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN home_draw_odds FLOAT"))
            print("✓ Added home_draw_odds column")
        except Exception as e:
            print(f"home_draw_odds: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN home_away_odds FLOAT"))
            print("✓ Added home_away_odds column")
        except Exception as e:
            print(f"home_away_odds: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN draw_away_odds FLOAT"))
            print("✓ Added draw_away_odds column")
        except Exception as e:
            print(f"draw_away_odds: {e}")
        
        # Both Teams to Score
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN gg_odds FLOAT"))
            print("✓ Added gg_odds column")
        except Exception as e:
            print(f"gg_odds: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN ng_odds FLOAT"))
            print("✓ Added ng_odds column")
        except Exception as e:
            print(f"ng_odds: {e}")
        
        # Over/Under 2.5
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN over25_odds FLOAT"))
            print("✓ Added over25_odds column")
        except Exception as e:
            print(f"over25_odds: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN under25_odds FLOAT"))
            print("✓ Added under25_odds column")
        except Exception as e:
            print(f"under25_odds: {e}")
        
        # Over/Under 1.5
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN over15_odds FLOAT"))
            print("✓ Added over15_odds column")
        except Exception as e:
            print(f"over15_odds: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN under15_odds FLOAT"))
            print("✓ Added under15_odds column")
        except Exception as e:
            print(f"under15_odds: {e}")
        
        # Over/Under 3.5
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN over35_odds FLOAT"))
            print("✓ Added over35_odds column")
        except Exception as e:
            print(f"over35_odds: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE matches ADD COLUMN under35_odds FLOAT"))
            print("✓ Added under35_odds column")
        except Exception as e:
            print(f"under35_odds: {e}")
        
        conn.commit()
    
    print("\n✅ Database migration completed!")
    print("New betting markets added to matches table")
