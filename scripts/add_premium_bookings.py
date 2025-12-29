"""
Script to add premium booking tables to the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.premium_booking import PremiumBooking, PremiumBookingPurchase

flask_app = create_app()

with flask_app.app_context():
    # Create the tables
    db.create_all()
    print("✓ Premium booking tables created successfully")
    print("  - premium_bookings")
    print("  - premium_booking_purchases")
