from app import create_app, db
from app.models import Bet, Match

app = create_app()

with app.app_context():
    # Check Universitario vs Sporting bet
    print("="*60)
    print("CHECKING: Universitario vs Sporting (AWAY)")
    print("="*60)
    bet = Bet.query.filter_by(id=110).first()
    matches = Match.query.filter(
        Match.home_team.like("%Universitario%")
    ).all()
    
    print(f"\nBet 110:")
    print(f"  Description: {bet.event_description}")
    print(f"  Selection: '{bet.selection}'")
    print(f"  Market: {bet.market_type}")
    print(f"  Status: {bet.status}")
    print(f"  Match ID: {bet.match_id}")
    
    print(f"\nMatches found:")
    for m in matches:
        print(f"  Match {m.id}: {m.home_team} {m.home_score}-{m.away_score} {m.away_team}")
        if bet.match_id == m.id:
            print(f"    ^^^ THIS IS THE LINKED MATCH ^^^")
            print(f"    Home score: {m.home_score}, Away score: {m.away_score}")
            print(f"    Away won? {m.away_score > m.home_score}")
            print(f"    Bet selected: '{bet.selection}'")
            print(f"    Should be WON: {m.away_score > m.home_score and bet.selection.lower() == 'away'}")
    
    # Check Cruizero vs Nice bet
    print("\n" + "="*60)
    print("CHECKING: Cruizero vs Nice (OVER 2.5)")
    print("="*60)
    bet2 = Bet.query.filter_by(id=128).first()
    match2 = Match.query.filter(
        Match.home_team.like("%Cruizero%"),
        Match.away_team.like("%Nice%")
    ).first()
    
    print(f"\nBet 128:")
    print(f"  Description: {bet2.event_description}")
    print(f"  Selection: '{bet2.selection}'")
    print(f"  Market: {bet2.market_type}")
    print(f"  Status: {bet2.status}")
    print(f"  Match ID: {bet2.match_id}")
    
    print(f"\nMatch:")
    print(f"  Match {match2.id}: {match2.home_team} {match2.home_score}-{match2.away_score} {match2.away_team}")
    total_goals = match2.home_score + match2.away_score
    print(f"  Total goals: {total_goals}")
    print(f"  Over 2.5? {total_goals > 2.5}")
    print(f"  Bet selected: '{bet2.selection}'")
    print(f"  Should be WON: {total_goals > 2.5 and bet2.selection.lower() == 'over2'}")
