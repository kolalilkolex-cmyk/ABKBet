from app import create_app, db
from app.models import Bet, Match

app = create_app()

with app.app_context():
    bet = Bet.query.get(110)
    m = Match.query.get(bet.match_id)
    
    print(f'Bet 110:')
    print(f'  Description: {bet.event_description}')
    print(f'  Selection: {bet.selection}, Status: {bet.status}')
    print(f'  Linked to Match {bet.match_id}: {m.home_team} {m.home_score}-{m.away_score} {m.away_team}')
    print(f'  Away won? {m.away_score > m.home_score}')
    
    # The bet description says "Jeju United vs Sporting" but it's linked to Jeju United match
    # where Sporting LOST (Jeju won 3-1)
    # But user probably meant "Universitario vs Sporting" where Sporting WON (1-3)
    
    print(f'\nChecking if there is a Universitario vs Sporting match:')
    correct_match = Match.query.filter(
        Match.home_team.like('%Universitario%'),
        Match.away_team.like('%Sporting%')
    ).first()
    
    if correct_match:
        print(f'  Match {correct_match.id}: {correct_match.home_team} {correct_match.home_score}-{correct_match.away_score} {correct_match.away_team}')
        print(f'  Away won? {correct_match.away_score > correct_match.home_score}')
        print(f'  If bet was for THIS match, should be: {"WON" if correct_match.away_score > correct_match.home_score else "LOST"}')
