"""
Script to update premium booking system with balance restrictions
Run this after deployment to ensure the system works correctly
"""

from app import create_app, db
from app.models import User, PremiumBooking, PremiumBookingPurchase

def update_premium_system():
    """Update premium booking system with new restrictions"""
    app = create_app('production')
    
    with app.app_context():
        print("="*60)
        print("PREMIUM BOOKING SYSTEM UPDATE")
        print("="*60)
        
        # Verify tables exist
        try:
            booking_count = PremiumBooking.query.count()
            purchase_count = PremiumBookingPurchase.query.count()
            print(f"\n✓ Premium tables exist")
            print(f"  - Premium Bookings: {booking_count}")
            print(f"  - Purchases: {purchase_count}")
        except Exception as e:
            print(f"\n✗ Premium tables not found: {e}")
            print("\nCreating tables...")
            db.create_all()
            print("✓ Tables created")
        
        # Check for users who might be affected
        BTC_PRICE_USD = 45000.0
        users = User.query.all()
        
        affected_users = []
        eligible_users = []
        
        for user in users:
            balance_usd = user.balance * BTC_PRICE_USD
            if balance_usd >= 250.0:
                eligible_users.append({
                    'username': user.username,
                    'balance_usd': balance_usd
                })
            else:
                affected_users.append({
                    'username': user.username,
                    'balance_usd': balance_usd
                })
        
        print(f"\n✓ User Balance Check:")
        print(f"  - Total users: {len(users)}")
        print(f"  - Eligible for premium codes (>= $250): {len(eligible_users)}")
        print(f"  - Must deposit first (< $250): {len(affected_users)}")
        
        if eligible_users:
            print(f"\n  Eligible users (>= $250):")
            for u in eligible_users[:5]:  # Show first 5
                print(f"    - {u['username']}: ${u['balance_usd']:.2f}")
        
        if affected_users:
            print(f"\n  Users who must deposit first (< $250):")
            for u in affected_users[:5]:  # Show first 5
                print(f"    - {u['username']}: ${u['balance_usd']:.2f} (needs ${250 - u['balance_usd']:.2f})")
        
        print("\n" + "="*60)
        print("PREMIUM RESTRICTIONS SUMMARY")
        print("="*60)
        print("\n1. Users with balance >= $250 can access premium codes")
        print("2. Users with balance < $250 must deposit first to unlock selections")
        print("3. After deposit reaches $250, user can purchase code")
        print("4. After purchase, selections become visible")
        print("\n" + "="*60)
        print("UPDATE COMPLETE")
        print("="*60)

if __name__ == '__main__':
    update_premium_system()
