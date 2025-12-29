"""Test script to verify admin games API returns data correctly"""
from run import flask_app
from app.models.virtual_game import VirtualGame

with flask_app.app_context():
    games = VirtualGame.query.all()
    print(f"✅ Total games in database: {len(games)}")
    
    if games:
        print("\n📊 First 5 games:")
        for game in games[:5]:
            print(f"  ID {game.id}: {game.home_team} vs {game.away_team}")
            print(f"    League: {game.league_name}")
            print(f"    Status: {game.status}")
            print(f"    Scheduled: {game.scheduled_time}")
            print(f"    to_dict() scheduled_time: {game.to_dict().get('scheduled_time')}")
            print()
        
        print("\n🔍 Testing to_dict() for all games:")
        games_dicts = [game.to_dict() for game in games]
        print(f"  All games have scheduled_time: {all('scheduled_time' in g for g in games_dicts)}")
        print(f"  All scheduled_times are not None: {all(g.get('scheduled_time') is not None for g in games_dicts)}")
        
        # Simulate API response
        print("\n📡 Simulated API response:")
        import json
        response = {
            'success': True,
            'games': games_dicts[:3]
        }
        print(json.dumps(response, indent=2, default=str))
