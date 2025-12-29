import requests

# Test the API endpoint
try:
    # Get token first (you'll need to use your actual token)
    # For now, let's just check the endpoint structure
    
    # You can also check what the backend returns
    from app import create_app, db
    from app.models.user import User
    from app.services.betting_service import BettingService
    
    app = create_app()
    with app.app_context():
        # Get alice user
        user = User.query.filter_by(username='alice').first()
        if user:
            betting_service = BettingService()
            active_bets = betting_service.get_active_bets(user)
            
            print(f"Found {len(active_bets)} active bets")
            print("\nFirst bet structure:")
            if active_bets:
                bet = active_bets[0]
                print(f"ID: {bet.id}")
                print(f"Amount: {bet.amount}")
                print(f"Odds: {bet.odds}")
                print(f"Event Description: {bet.event_description}")
                print(f"Booking Code: {bet.booking_code}")
                print(f"Status: {bet.status}")
                print(f"Is Cashed Out: {bet.is_cashed_out}")
                print(f"Created At: {bet.created_at}")
        else:
            print("User 'alice' not found")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
