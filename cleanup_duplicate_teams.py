"""
Emergency cleanup script to fix duplicate teams in Premier League
Run this on PythonAnywhere to clean up the 80 teams down to 20
"""
from run import flask_app
from app.models.virtual_game import VirtualLeague, VirtualTeam, VirtualGame
from app.extensions import db

with flask_app.app_context():
    print("=" * 60)
    print("CLEANUP: Fixing Duplicate Teams")
    print("=" * 60)
    
    # Get Premier League
    premier = VirtualLeague.query.filter_by(name='Premier League').first()
    if not premier:
        print("❌ Premier League not found")
        exit(1)
    
    print(f"\n📊 Current state:")
    teams = VirtualTeam.query.filter_by(league_id=premier.id).all()
    print(f"   Premier League has {len(teams)} teams")
    
    if len(teams) <= 20:
        print("✅ Premier League already has 20 or fewer teams. No cleanup needed.")
        exit(0)
    
    # Get unique team names and keep only first occurrence
    correct_teams = [
        'Man City', 'Arsenal', 'Liverpool', 'Aston Villa', 'Tottenham', 
        'Chelsea', 'Newcastle', 'Man United', 'West Ham', 'Brighton',
        'Crystal Palace', 'Fulham', 'Brentford', 'Everton', 'Nottingham',
        'Wolves', 'Bournemouth', 'Luton Town', 'Burnley', 'Sheffield Utd'
    ]
    
    print(f"\n🔍 Finding duplicates...")
    teams_to_keep = []
    teams_to_delete = []
    
    for team_name in correct_teams:
        # Find all teams with this name
        matching = [t for t in teams if t.name == team_name]
        if matching:
            teams_to_keep.append(matching[0])  # Keep first one
            teams_to_delete.extend(matching[1:])  # Delete rest
    
    # Also delete any teams not in the correct list
    for team in teams:
        if team.name not in correct_teams and team not in teams_to_delete:
            teams_to_delete.append(team)
    
    print(f"   ✅ Keeping: {len(teams_to_keep)} unique teams")
    print(f"   ❌ Deleting: {len(teams_to_delete)} duplicate teams")
    
    if not teams_to_delete:
        print("\n✅ No duplicates found!")
        exit(0)
    
    # Delete games involving duplicate teams first
    print(f"\n🗑️  Deleting games with duplicate teams...")
    games_deleted = 0
    for team in teams_to_delete:
        games = VirtualGame.query.filter(
            (VirtualGame.home_team_id == team.id) | 
            (VirtualGame.away_team_id == team.id)
        ).all()
        for game in games:
            db.session.delete(game)
            games_deleted += 1
    
    print(f"   Deleted {games_deleted} games")
    
    # Now delete duplicate teams
    print(f"\n🗑️  Deleting {len(teams_to_delete)} duplicate teams...")
    for team in teams_to_delete:
        print(f"   - Deleting: {team.name} (ID: {team.id})")
        db.session.delete(team)
    
    # Commit changes
    db.session.commit()
    
    # Verify
    final_count = VirtualTeam.query.filter_by(league_id=premier.id).count()
    print(f"\n✅ Cleanup complete!")
    print(f"   Premier League now has {final_count} teams")
    
    if final_count == 20:
        print("   ✨ Perfect! Exactly 20 teams as expected.")
    else:
        print(f"   ⚠️  Warning: Expected 20 teams, got {final_count}")
    
    print("\n" + "=" * 60)
