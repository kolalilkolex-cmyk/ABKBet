"""
Database migration script for virtual games

Run this script to create the virtual games tables in your database.
"""

from app.extensions import db
from app import create_app
from app.models.virtual_game import VirtualLeague, VirtualTeam, VirtualGame
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_virtual_game_tables():
    """Create virtual game tables"""
    try:
        app = create_app()
        
        with app.app_context():
            logger.info("Creating virtual game tables...")
            
            # Create tables
            db.create_all()
            
            logger.info("✅ Virtual game tables created successfully!")
            
            # Print created tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            virtual_tables = [t for t in tables if 'virtual' in t.lower()]
            
            if virtual_tables:
                logger.info(f"Created tables: {', '.join(virtual_tables)}")
            else:
                logger.warning("No virtual tables found. Make sure models are imported correctly.")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Virtual Games Database Migration")
    print("="*60 + "\n")
    
    success = create_virtual_game_tables()
    
    if success:
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Access the admin panel at /virtual-games-admin.html")
        print("2. Run Quick Setup to create leagues and teams")
        print("3. Schedule games and start managing virtual games")
        print("\nUsers can view and bet on games at /virtual-games.html")
    else:
        print("\n" + "="*60)
        print("❌ Migration failed. Check the error messages above.")
        print("="*60)
