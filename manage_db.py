#!/usr/bin/env python
"""
Database initialization and management script
Run this to initialize or reset the database
"""

import os
import sys
from run import create_app
from app.models import db

def init_db():
    """Initialize database"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database initialized successfully!")

def drop_db():
    """Drop all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Database dropped successfully!")

def reset_db():
    """Reset database (drop and recreate)"""
    print("Resetting database...")
    drop_db()
    init_db()
    print("Database reset successfully!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py [init|drop|reset]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'init':
        init_db()
    elif command == 'drop':
        drop_db()
    elif command == 'reset':
        reset_db()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
