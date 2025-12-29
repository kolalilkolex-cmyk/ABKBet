"""
Add real matches to ABKBet database
Run this on PythonAnywhere: python add_real_matches.py
"""
from app import create_app, db
from app.models import Match
from datetime import datetime

def add_real_matches():
    """Add all real matches to database"""
    app = create_app('production')
    
    with app.app_context():
        print("\n" + "="*70)
        print("⚽ Adding Real Matches to Database")
        print("="*70 + "\n")
        
        matches = [
            # Premier League
            {'league': 'English Premier League', 'home': 'Brighton & Hove Albion', 'away': 'West Ham United', 'date': '2025-12-07 15:00', 'odds': (1.54, 4.30, 5.70)},
            {'league': 'English Premier League', 'home': 'Fulham', 'away': 'Crystal Palace', 'date': '2025-12-07 17:30', 'odds': (2.59, 3.24, 2.78)},
            {'league': 'English Premier League', 'home': 'Wolves', 'away': 'Manchester United', 'date': '2025-12-07 21:00', 'odds': (4.59, 4.00, 1.72)},
            {'league': 'English Premier League', 'home': 'Liverpool', 'away': 'Brighton & Hove Albion', 'date': '2025-12-13 16:00', 'odds': (1.70, 4.14, 4.64)},
            {'league': 'English Premier League', 'home': 'Chelsea', 'away': 'Everton', 'date': '2025-12-13 16:00', 'odds': (1.59, 4.06, 5.50)},
            {'league': 'English Premier League', 'home': 'Burnley', 'away': 'Fulham', 'date': '2025-12-13 18:30', 'odds': (3.80, 3.48, 1.99)},
            {'league': 'English Premier League', 'home': 'Arsenal', 'away': 'Wolves', 'date': '2025-12-13 21:00', 'odds': (1.18, 6.10, 21.00)},
            {'league': 'English Premier League', 'home': 'West Ham United', 'away': 'Aston Villa', 'date': '2025-12-14 15:00', 'odds': (3.82, 3.62, 1.94)},
            {'league': 'English Premier League', 'home': 'Crystal Palace', 'away': 'Manchester City', 'date': '2025-12-14 15:00', 'odds': (4.19, 3.74, 1.85)},
            {'league': 'English Premier League', 'home': 'Nottingham Forest', 'away': 'Tottenham', 'date': '2025-12-14 15:00', 'odds': (2.38, 3.42, 2.93)},
            {'league': 'English Premier League', 'home': 'Sunderland', 'away': 'Leeds United', 'date': '2025-12-14 15:00', 'odds': (3.59, 3.36, 2.11)},
            {'league': 'English Premier League', 'home': 'Brentford', 'away': 'Crystal Palace', 'date': '2025-12-14 17:30', 'odds': (2.00, 3.56, 3.66)},
            
            # La Liga
            {'league': 'Spanish La Liga', 'home': 'Elche', 'away': 'Girona', 'date': '2025-12-07 14:00', 'odds': (2.17, 3.36, 3.36)},
            {'league': 'Spanish La Liga', 'home': 'Valencia', 'away': 'Sevilla', 'date': '2025-12-07 16:15', 'odds': (2.05, 3.42, 3.66)},
            {'league': 'Spanish La Liga', 'home': 'Espanyol', 'away': 'Rayo Vallecano', 'date': '2025-12-07 18:30', 'odds': (2.29, 3.26, 3.20)},
            {'league': 'Spanish La Liga', 'home': 'Real Madrid', 'away': 'Celta Vigo', 'date': '2025-12-07 21:00', 'odds': (1.25, 5.90, 10.50)},
            {'league': 'Spanish La Liga', 'home': 'Osasuna', 'away': 'Levante', 'date': '2025-12-08 21:00', 'odds': (1.71, 3.76, 4.90)},
            {'league': 'Spanish La Liga', 'home': 'Real Sociedad', 'away': 'Girona', 'date': '2025-12-12 21:00', 'odds': (1.79, 3.84, 4.85)},
            {'league': 'Spanish La Liga', 'home': 'Atletico Madrid', 'away': 'Valencia', 'date': '2025-12-13 14:00', 'odds': (1.29, 5.36, 10.50)},
            {'league': 'Spanish La Liga', 'home': 'Mallorca', 'away': 'Elche', 'date': '2025-12-13 16:15', 'odds': (2.26, 3.19, 3.36)},
            {'league': 'Spanish La Liga', 'home': 'Barcelona', 'away': 'Osasuna', 'date': '2025-12-13 18:30', 'odds': (1.22, 6.07, 11.00)},
            {'league': 'Spanish La Liga', 'home': 'Getafe', 'away': 'Espanyol', 'date': '2025-12-13 21:00', 'odds': (2.46, 2.96, 3.22)},
            
            # Serie A
            {'league': 'Italian Serie A', 'home': 'Cagliari', 'away': 'Roma', 'date': '2025-12-07 15:00', 'odds': (5.55, 3.70, 1.65)},
            {'league': 'Italian Serie A', 'home': 'Lazio', 'away': 'Bologna', 'date': '2025-12-07 18:00', 'odds': (2.58, 3.02, 2.99)},
            {'league': 'Italian Serie A', 'home': 'Napoli', 'away': 'Juventus', 'date': '2025-12-07 20:45', 'odds': (2.51, 2.98, 3.13)},
            {'league': 'Italian Serie A', 'home': 'Pisa 1909', 'away': 'Parma', 'date': '2025-12-08 15:00', 'odds': (2.49, 2.98, 3.16)},
            {'league': 'Italian Serie A', 'home': 'Udinese', 'away': 'Genoa', 'date': '2025-12-08 18:00', 'odds': (2.47, 2.99, 3.17)},
            {'league': 'Italian Serie A', 'home': 'Torino', 'away': 'AC Milan', 'date': '2025-12-08 20:45', 'odds': (2.45, 3.00, 3.19)},
            
            # Bundesliga
            {'league': 'German Bundesliga', 'home': 'Hamburger SV', 'away': 'Werder Bremen', 'date': '2025-12-07 15:30', 'odds': (2.33, 3.52, 2.94)},
            {'league': 'German Bundesliga', 'home': 'Borussia Dortmund', 'away': 'Hoffenheim', 'date': '2025-12-07 17:30', 'odds': (1.59, 4.40, 5.05)},
            {'league': 'German Bundesliga', 'home': 'Union Berlin', 'away': 'RB Leipzig', 'date': '2025-12-12 20:30', 'odds': (3.46, 3.56, 2.06)},
            {'league': 'German Bundesliga', 'home': 'Eintracht Frankfurt', 'away': 'Augsburg', 'date': '2025-12-13 15:30', 'odds': (1.63, 4.24, 4.88)},
            {'league': 'German Bundesliga', 'home': 'Borussia Monchengladbach', 'away': 'Wolfsburg', 'date': '2025-12-13 15:30', 'odds': (2.00, 3.76, 3.56)},
            {'league': 'German Bundesliga', 'home': 'St. Pauli', 'away': 'Heidenheim', 'date': '2025-12-13 15:30', 'odds': (1.84, 3.50, 4.44)},
            {'league': 'German Bundesliga', 'home': 'Hoffenheim', 'away': 'Hamburger SV', 'date': '2025-12-13 15:30', 'odds': (1.74, 4.10, 4.20)},
            {'league': 'German Bundesliga', 'home': 'Bayer Leverkusen', 'away': 'FC Koln', 'date': '2025-12-13 18:30', 'odds': (1.52, 4.60, 5.60)},
            {'league': 'German Bundesliga', 'home': 'Freiburg', 'away': 'Borussia Dortmund', 'date': '2025-12-14 15:30', 'odds': (3.30, 3.44, 2.16)},
            {'league': 'German Bundesliga', 'home': 'Bayern Munich', 'away': 'Mainz 05', 'date': '2025-12-14 17:30', 'odds': (1.12, 9.70, 19.00)},
            
            # Ligue 1
            {'league': 'French Ligue 1', 'home': 'Nice', 'away': 'Angers SCO', 'date': '2025-12-07 15:00', 'odds': (1.92, 3.64, 3.86)},
            {'league': 'French Ligue 1', 'home': 'Le Havre', 'away': 'Paris FC', 'date': '2025-12-07 17:15', 'odds': (2.71, 3.24, 2.65)},
            {'league': 'French Ligue 1', 'home': 'Auxerre', 'away': 'Metz', 'date': '2025-12-07 17:15', 'odds': (1.95, 3.54, 3.86)},
            {'league': 'French Ligue 1', 'home': 'Lorient', 'away': 'Lyon', 'date': '2025-12-07 20:45', 'odds': (3.15, 3.56, 2.19)},
            {'league': 'French Ligue 1', 'home': 'Angers SCO', 'away': 'Nantes', 'date': '2025-12-12 20:45', 'odds': (2.37, 3.15, 3.16)},
            {'league': 'French Ligue 1', 'home': 'Stade Rennais', 'away': 'Stade Brestois', 'date': '2025-12-13 17:00', 'odds': (1.84, 3.70, 4.16)},
            {'league': 'French Ligue 1', 'home': 'Metz', 'away': 'Paris Saint-Germain', 'date': '2025-12-13 19:00', 'odds': (11.00, 6.20, 1.24)},
            {'league': 'French Ligue 1', 'home': 'Paris FC', 'away': 'Toulouse', 'date': '2025-12-13 21:05', 'odds': (2.40, 3.30, 2.99)},
            {'league': 'French Ligue 1', 'home': 'Lyon', 'away': 'Le Havre', 'date': '2025-12-14 15:00', 'odds': (1.53, 4.10, 6.25)},
            {'league': 'French Ligue 1', 'home': 'Marseille', 'away': 'AS Monaco', 'date': '2025-12-14 20:45', 'odds': (1.85, 3.96, 4.16)},
            
            # Champions League
            {'league': 'UEFA Champions League', 'home': 'Kairat', 'away': 'Olympiacos', 'date': '2025-12-09 16:30', 'odds': (6.45, 4.30, 1.50)},
            {'league': 'UEFA Champions League', 'home': 'Bayern Munich', 'away': 'Sporting CP', 'date': '2025-12-09 18:45', 'odds': (1.25, 6.30, 10.50)},
            {'league': 'UEFA Champions League', 'home': 'Atalanta', 'away': 'Chelsea', 'date': '2025-12-09 21:00', 'odds': (3.35, 3.54, 2.10)},
            {'league': 'UEFA Champions League', 'home': 'Barcelona', 'away': 'Eintracht Frankfurt', 'date': '2025-12-09 21:00', 'odds': (1.15, 8.30, 14.05)},
            {'league': 'UEFA Champions League', 'home': 'Inter Milan', 'away': 'Liverpool', 'date': '2025-12-09 21:00', 'odds': (2.15, 3.64, 3.10)},
            {'league': 'UEFA Champions League', 'home': 'PSV', 'away': 'Atletico Madrid', 'date': '2025-12-09 21:00', 'odds': (3.11, 3.82, 2.13)},
            {'league': 'UEFA Champions League', 'home': 'Athletic Bilbao', 'away': 'Paris Saint-Germain', 'date': '2025-12-10 21:00', 'odds': (5.65, 4.10, 1.57)},
            {'league': 'UEFA Champions League', 'home': 'Benfica', 'away': 'Napoli', 'date': '2025-12-10 21:00', 'odds': (2.31, 3.32, 3.11)},
            {'league': 'UEFA Champions League', 'home': 'Club Brugge', 'away': 'Arsenal', 'date': '2025-12-10 21:00', 'odds': (9.00, 5.15, 1.33)},
            {'league': 'UEFA Champions League', 'home': 'Real Madrid', 'away': 'Manchester City', 'date': '2025-12-10 21:00', 'odds': (2.26, 3.78, 2.88)},
        ]
        
        added = 0
        skipped = 0
        
        for match_data in matches:
            # Check if match already exists
            existing = Match.query.filter_by(
                league=match_data['league'],
                home_team=match_data['home'],
                away_team=match_data['away']
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Parse date
            match_date = datetime.strptime(match_data['date'], '%Y-%m-%d %H:%M')
            
            # Create match
            match = Match(
                league=match_data['league'],
                home_team=match_data['home'],
                away_team=match_data['away'],
                match_date=match_date,
                home_odds=match_data['odds'][0],
                draw_odds=match_data['odds'][1],
                away_odds=match_data['odds'][2],
                status='scheduled'
            )
            
            db.session.add(match)
            added += 1
            print(f"✓ {match_data['league']}: {match_data['home']} vs {match_data['away']}")
        
        db.session.commit()
        
        print("\n" + "="*70)
        print(f"✅ Added {added} new matches")
        if skipped > 0:
            print(f"ℹ️  Skipped {skipped} duplicate matches")
        print(f"📊 Total matches in database: {Match.query.count()}")
        print("="*70)
        print("\n🔄 Reload your web app to see the new matches!")
        print("🌐 Visit: https://abkbet.pythonanywhere.com\n")

if __name__ == '__main__':
    add_real_matches()
