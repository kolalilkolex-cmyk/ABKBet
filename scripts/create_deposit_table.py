"""Add deposit_requests table for manual approval system"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Create deposit_requests table
    db.session.execute(text("""
    CREATE TABLE IF NOT EXISTS deposit_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount FLOAT NOT NULL,
        payment_method VARCHAR(50) NOT NULL,
        transaction_reference VARCHAR(255) NOT NULL,
        payment_proof TEXT,
        status VARCHAR(20) DEFAULT 'pending',
        admin_notes TEXT,
        approved_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (approved_by) REFERENCES users(id)
    )
    """))
    
    db.session.commit()
    print("✅ deposit_requests table created successfully!")
