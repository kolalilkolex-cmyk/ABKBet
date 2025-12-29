import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Add halftime score columns to matches table
        with db.engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT COUNT(*) as count FROM pragma_table_info('matches') 
                WHERE name IN ('ht_home_score', 'ht_away_score', 'ht_status')
            """))
            existing_count = result.fetchone()[0]
            
            if existing_count == 0:
                print("Adding halftime score columns...")
                conn.execute(text("""
                    ALTER TABLE matches ADD COLUMN ht_home_score INTEGER
                """))
                conn.execute(text("""
                    ALTER TABLE matches ADD COLUMN ht_away_score INTEGER
                """))
                conn.execute(text("""
                    ALTER TABLE matches ADD COLUMN ht_status VARCHAR(20) DEFAULT 'pending'
                """))
                conn.commit()
                print("✅ Halftime score columns added successfully!")
            else:
                print("ℹ️  Halftime score columns already exist")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
