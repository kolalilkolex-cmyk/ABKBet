"""
Create matches table in the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Match

def create_matches_table():
    """Create the matches table"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # Create matches table
            db.create_all()
            print("✅ Matches table created successfully!")
            
            # Verify table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'matches' in tables:
                print(f"✅ Verified: 'matches' table exists")
                print(f"   Total tables: {len(tables)}")
            else:
                print("❌ Warning: 'matches' table not found after creation")
            
        except Exception as e:
            print(f"❌ Error creating matches table: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("Creating matches table...")
    success = create_matches_table()
    sys.exit(0 if success else 1)
