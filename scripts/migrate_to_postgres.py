"""
PostgreSQL Migration Script
Migrates data from SQLite to PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database(sqlite_uri, postgres_uri):
    """
    Migrate all data from SQLite to PostgreSQL
    
    Args:
        sqlite_uri: SQLite database URI (e.g., 'sqlite:///instance/betting.db')
        postgres_uri: PostgreSQL database URI (e.g., 'postgresql://user:pass@localhost/dbname')
    """
    
    logger.info("Starting database migration from SQLite to PostgreSQL...")
    
    # Create engines
    sqlite_engine = create_engine(sqlite_uri)
    postgres_engine = create_engine(postgres_uri)
    
    # Reflect metadata from SQLite
    sqlite_metadata = MetaData()
    sqlite_metadata.reflect(bind=sqlite_engine)
    
    # Create all tables in PostgreSQL (should already exist from migrations)
    postgres_metadata = MetaData()
    postgres_metadata.reflect(bind=postgres_engine)
    
    # Create sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SqliteSession()
    postgres_session = PostgresSession()
    
    try:
        # Get list of tables to migrate
        tables_to_migrate = [
            'users',
            'bets',
            'game_picks',
            'alembic_version'
        ]
        
        total_migrated = 0
        
        for table_name in tables_to_migrate:
            if table_name not in sqlite_metadata.tables:
                logger.warning(f"Table {table_name} not found in SQLite database, skipping")
                continue
            
            logger.info(f"Migrating table: {table_name}")
            
            # Get table objects
            sqlite_table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)
            postgres_table = Table(table_name, postgres_metadata, autoload_with=postgres_engine)
            
            # Read all rows from SQLite
            sqlite_conn = sqlite_engine.connect()
            rows = sqlite_conn.execute(sqlite_table.select()).fetchall()
            
            if not rows:
                logger.info(f"  No rows found in {table_name}")
                continue
            
            logger.info(f"  Found {len(rows)} rows to migrate")
            
            # Convert rows to dictionaries
            row_dicts = []
            for row in rows:
                row_dict = dict(row._mapping)
                row_dicts.append(row_dict)
            
            # Insert into PostgreSQL
            postgres_conn = postgres_engine.connect()
            if row_dicts:
                postgres_conn.execute(postgres_table.insert(), row_dicts)
                postgres_conn.commit()
                logger.info(f"  Successfully migrated {len(row_dicts)} rows")
                total_migrated += len(row_dicts)
            
            postgres_conn.close()
            sqlite_conn.close()
        
        logger.info(f"\n✅ Migration completed successfully!")
        logger.info(f"Total rows migrated: {total_migrated}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        postgres_session.rollback()
        return False
        
    finally:
        sqlite_session.close()
        postgres_session.close()


def verify_migration(sqlite_uri, postgres_uri):
    """Verify that migration was successful by comparing row counts"""
    
    logger.info("\nVerifying migration...")
    
    sqlite_engine = create_engine(sqlite_uri)
    postgres_engine = create_engine(postgres_uri)
    
    sqlite_metadata = MetaData()
    sqlite_metadata.reflect(bind=sqlite_engine)
    
    postgres_metadata = MetaData()
    postgres_metadata.reflect(bind=postgres_engine)
    
    all_match = True
    
    for table_name in sqlite_metadata.tables:
        if table_name == 'alembic_version':
            continue
            
        sqlite_table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)
        postgres_table = Table(table_name, postgres_metadata, autoload_with=postgres_engine)
        
        sqlite_conn = sqlite_engine.connect()
        postgres_conn = postgres_engine.connect()
        
        sqlite_count = sqlite_conn.execute(sqlite_table.count()).scalar()
        postgres_count = postgres_conn.execute(postgres_table.count()).scalar()
        
        if sqlite_count == postgres_count:
            logger.info(f"✅ {table_name}: {sqlite_count} rows (match)")
        else:
            logger.error(f"❌ {table_name}: SQLite={sqlite_count}, PostgreSQL={postgres_count} (mismatch!)")
            all_match = False
        
        sqlite_conn.close()
        postgres_conn.close()
    
    if all_match:
        logger.info("\n✅ Verification passed: All tables match!")
    else:
        logger.error("\n❌ Verification failed: Some tables have mismatched row counts")
    
    return all_match


if __name__ == '__main__':
    # Example usage
    # Update these URIs with your actual database locations
    
    SQLITE_URI = os.getenv('SQLITE_URI', 'sqlite:///instance/betting.db')
    POSTGRES_URI = os.getenv('POSTGRES_URI', 'postgresql://username:password@localhost:5432/abkbet')
    
    print("=" * 80)
    print("ABKBet Database Migration Tool")
    print("=" * 80)
    print(f"\nSource (SQLite): {SQLITE_URI}")
    print(f"Target (PostgreSQL): {POSTGRES_URI}")
    print("\n⚠️  WARNING: This will copy all data from SQLite to PostgreSQL")
    print("Make sure you have:")
    print("  1. Created the PostgreSQL database")
    print("  2. Run Flask migrations (flask db upgrade)")
    print("  3. Backed up your data")
    
    response = input("\nContinue with migration? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Perform migration
    success = migrate_database(SQLITE_URI, POSTGRES_URI)
    
    if success:
        # Verify migration
        verify_migration(SQLITE_URI, POSTGRES_URI)
    else:
        logger.error("Migration failed. Please check the errors above.")
        sys.exit(1)
