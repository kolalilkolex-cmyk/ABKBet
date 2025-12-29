"""
Multi-Sport API Service - API-Sports Integration
Supports: Football, Basketball, Baseball, Hockey, NBA, NFL, Rugby, Volleyball, etc.
Fetches live matches, odds, and updates database
"""

import requests
import logging
import random
from datetime import datetime, timedelta
from flask import current_app
from app.extensions import db
from app.models import Match, MatchStatus

logger = logging.getLogger(__name__)


class FootballAPIService:
    """Service to interact with API-Sports for multiple sports"""
    
    # All sport endpoints
    SPORT_ENDPOINTS = {
        'football': 'https://v3.football.api-sports.io',
        'afl': 'https://v1.afl.api-sports.io',
        'baseball': 'https://v1.baseball.api-sports.io',
        'basketball': 'https://v1.basketball.api-sports.io',
        'formula1': 'https://v1.formula-1.api-sports.io',
        'handball': 'https://v1.handball.api-sports.io',
        'hockey': 'https://v1.hockey.api-sports.io',
        'mma': 'https://v1.mma.api-sports.io',
        'nba': 'https://v2.nba.api-sports.io',
        'nfl': 'https://v1.american-football.api-sports.io',
        'rugby': 'https://v1.rugby.api-sports.io',
        'volleyball': 'https://v1.volleyball.api-sports.io'
    }
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    # Popular leagues by country for football
    FOOTBALL_LEAGUES = {
        'England': [39, 40, 41, 42],  # Premier League, Championship, League One, League Two
        'Spain': [140, 141],  # La Liga, Segunda Division
        'Germany': [78, 79],  # Bundesliga, 2. Bundesliga
        'Italy': [135, 136],  # Serie A, Serie B
        'France': [61, 62],  # Ligue 1, Ligue 2
        'UEFA': [2, 3, 848],  # Champions League, Europa League, Conference League
        'International': [1, 4, 5]  # World Cup, Euro Championship, Nations League
    }
    
    def __init__(self):
        self.api_key = None
        self.headers = None
    
    def initialize(self, api_key):
        """Initialize the service with API key"""
        self.api_key = api_key
        self.headers = {
            'x-apisports-key': api_key
        }
    
    def _make_request(self, endpoint, params=None, sport='football'):
        """Make a request to the API for any sport"""
        if not self.api_key:
            logger.error("API key not configured")
            return None
        
        # Get the correct base URL for the sport
        base_url = self.SPORT_ENDPOINTS.get(sport, self.BASE_URL)
        
        try:
            url = f"{base_url}/{endpoint}"
            logger.info(f"API Request ({sport}): {url} with params: {params}")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('errors') and len(data.get('errors', [])) > 0:
                logger.error(f"API returned errors: {data['errors']}")
                return None
            
            logger.info(f"API Response: {data.get('results', 0)} results")
            return data.get('response', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {sport}: {e}")
            return None
    
    def get_live_matches(self, sport='football'):
        """Get all live matches for any sport"""
        if sport == 'football':
            return self._make_request('fixtures', {'live': 'all'}, sport='football')
        elif sport == 'basketball':
            return self._make_request('games', {'live': 'all'}, sport='basketball')
        elif sport == 'nba':
            return self._make_request('games', {'live': 'all'}, sport='nba')
        elif sport == 'hockey':
            return self._make_request('games', {'live': 'all'}, sport='hockey')
        else:
            return []
    
    def get_today_matches(self, league_id=None):
        """Get today's matches, optionally filtered by league"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        params = {'date': today}
        if league_id:
            params['league'] = league_id
        
        # Also get live matches
        logger.info("Fetching today's and live matches...")
        fixtures = self._make_request('fixtures', params)
        live_fixtures = self._make_request('fixtures', {'live': 'all'})
        
        # Combine both
        all_fixtures = fixtures if fixtures else []
        if live_fixtures:
            # Add live matches that aren't already in today's list
            live_ids = {f.get('fixture', {}).get('id') for f in live_fixtures}
            today_ids = {f.get('fixture', {}).get('id') for f in all_fixtures}
            for live_match in live_fixtures:
                if live_match.get('fixture', {}).get('id') not in today_ids:
                    all_fixtures.append(live_match)
        
        return all_fixtures
    
    def get_all_sports_today(self):
        """Get today's matches from ALL sports"""
        all_matches = []
        
        # Football (soccer)
        football = self.get_today_matches()
        if football:
            all_matches.extend(football)
            logger.info(f"Fetched {len(football)} football matches")
        
        # Basketball
        basketball = self._get_sport_today('basketball')
        if basketball:
            all_matches.extend(basketball)
            logger.info(f"Fetched {len(basketball)} basketball matches")
        
        # NBA
        nba = self._get_sport_today('nba')
        if nba:
            all_matches.extend(nba)
            logger.info(f"Fetched {len(nba)} NBA matches")
        
        # Baseball
        baseball = self._get_sport_today('baseball')
        if baseball:
            all_matches.extend(baseball)
            logger.info(f"Fetched {len(baseball)} baseball matches")
        
        # Hockey
        hockey = self._get_sport_today('hockey')
        if hockey:
            all_matches.extend(hockey)
            logger.info(f"Fetched {len(hockey)} hockey matches")
        
        # NFL/NCAA
        nfl = self._get_sport_today('nfl')
        if nfl:
            all_matches.extend(nfl)
            logger.info(f"Fetched {len(nfl)} NFL/NCAA matches")
        
        logger.info(f"Total matches across all sports: {len(all_matches)}")
        return all_matches
    
    def _get_sport_today(self, sport):
        """Get today's matches for a specific sport"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        try:
            if sport == 'basketball':
                games = self._make_request('games', {'date': today}, sport='basketball')
            elif sport == 'nba':
                games = self._make_request('games', {'date': today}, sport='nba')
            elif sport == 'baseball':
                games = self._make_request('games', {'date': today, 'league': 1}, sport='baseball')
            elif sport == 'hockey':
                games = self._make_request('games', {'date': today, 'league': 57}, sport='hockey')
            elif sport == 'nfl':
                games = self._make_request('games', {'date': today}, sport='nfl')
            else:
                return []
            
            if not games:
                return []
            
            # Process games into standard format
            return self._process_sport_games(games, sport)
        except Exception as e:
            logger.error(f"Error fetching {sport} matches: {e}")
            return []
    
    def _process_sport_games(self, games, sport):
        """Convert sport games to standard match format"""
        matches = []
        
        for game in games[:30]:  # Limit to 30 per sport
            try:
                teams = game.get('teams', {})
                league = game.get('league', {})
                country = league.get('country', {}).get('name', '') if isinstance(league.get('country'), dict) else league.get('country', '')
                league_name = league.get('name', sport.upper())
                
                # Create unique league name with country and sport
                if country:
                    full_league = f"{league_name} ({country}) - {sport.upper()}"
                else:
                    full_league = f"{league_name} - {sport.upper()}"
                
                # Generate varied realistic odds
                home_odds = round(random.uniform(1.5, 3.5), 2)
                away_odds = round(random.uniform(1.5, 3.5), 2)
                draw_odds = round(random.uniform(2.8, 4.5), 2) if sport == 'football' else None
                
                match_data = {
                    'fixture': {'id': game.get('id')},
                    'teams': teams,
                    'league': {'name': full_league, 'country': country},
                    'fixture_info': {
                        'date': game.get('date'),
                        'status': {'short': game.get('status', {}).get('short', 'NS')}
                    },
                    'goals': game.get('scores', {}).get('home', {}),
                    'home_odds': home_odds,
                    'draw_odds': draw_odds,
                    'away_odds': away_odds
                }
                
                matches.append(game)  # Return original format for sync
                
            except Exception as e:
                logger.error(f"Error processing {sport} game: {e}")
                continue
        
        return games  # Return original for now
    
    def get_upcoming_matches(self, days=7, league_ids=None):
        """Get upcoming matches for the next N days"""
        # For now, just get today's matches
        return self.get_all_sports_today()
    
    def get_match_odds(self, fixture_id):
        """Get odds for a specific match"""
        return self._make_request('odds', {'fixture': fixture_id})
    
    def sync_matches_to_database(self, matches_data):
        """
        Sync matches from API to database
        Returns: (created, updated) counts
        """
        if not matches_data:
            logger.warning("No matches data to sync")
            return 0, 0
        
        created = 0
        updated = 0
        
        for fixture in matches_data:
            try:
                fixture_id = fixture.get('fixture', {}).get('id')
                if not fixture_id:
                    continue
                
                teams = fixture.get('teams', {})
                home_team = teams.get('home', {}).get('name', 'Unknown')
                away_team = teams.get('away', {}).get('name', 'Unknown')
                
                league = fixture.get('league', {})
                league_name = league.get('name', 'Unknown League')
                country = league.get('country', '')
                
                # Make league name unique by including country
                if country:
                    full_league_name = f"{league_name} ({country})"
                else:
                    full_league_name = league_name
                
                fixture_info = fixture.get('fixture', {})
                match_date_str = fixture_info.get('date')
                match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00')) if match_date_str else datetime.utcnow()
                
                status = fixture_info.get('status', {}).get('short', 'NS')
                match_status = self._map_api_status_to_db_status(status)
                
                # Get scores
                goals = fixture.get('goals', {})
                home_score = goals.get('home')
                away_score = goals.get('away')
                
                # Check if match exists
                existing_match = Match.query.filter_by(api_fixture_id=fixture_id).first()
                
                if existing_match:
                    # Update existing match
                    existing_match.home_team = home_team
                    existing_match.away_team = away_team
                    existing_match.league = full_league_name
                    existing_match.match_date = match_date
                    existing_match.status = match_status
                    existing_match.home_score = home_score
                    existing_match.away_score = away_score
                    existing_match.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Create new match with default odds
                    # Generate realistic random odds instead of fixed values
                    import random
                    home_odds = round(random.uniform(1.5, 3.5), 2)
                    away_odds = round(random.uniform(1.5, 3.5), 2)
                    draw_odds = round(random.uniform(2.8, 4.5), 2)
                    
                    new_match = Match(
                        home_team=home_team,
                        away_team=away_team,
                        league=full_league_name,
                        match_date=match_date,
                        status=match_status,
                        home_score=home_score,
                        away_score=away_score,
                        home_odds=home_odds,
                        draw_odds=draw_odds,
                        away_odds=away_odds,
                        over25_odds=round(random.uniform(1.6, 2.2), 2),
                        under25_odds=round(random.uniform(1.6, 2.2), 2),
                        gg_odds=round(random.uniform(1.6, 2.0), 2),
                        ng_odds=round(random.uniform(1.7, 2.1), 2),
                        is_manual=False,
                        api_fixture_id=fixture_id
                    )
                    db.session.add(new_match)
                    created += 1
            
            except Exception as e:
                logger.error(f"Error syncing match {fixture_id}: {e}")
                continue
        
        try:
            db.session.commit()
            logger.info(f"Synced matches: {created} created, {updated} updated")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database commit failed: {e}")
            return 0, 0
        
        return created, updated
    
    def update_match_odds(self, fixture_id, db_match_id):
        """
        Fetch and update odds for a specific match
        Returns: True if updated, False otherwise
        """
        odds_data = self.get_match_odds(fixture_id)
        
        if not odds_data:
            logger.warning(f"No odds data for fixture {fixture_id}")
            return False
        
        try:
            match = Match.query.get(db_match_id)
            if not match:
                logger.error(f"Match {db_match_id} not found in database")
                return False
            
            # API-Football returns odds from multiple bookmakers
            # We'll use the first bookmaker's odds or average them
            for odds_entry in odds_data:
                bookmakers = odds_entry.get('bookmakers', [])
                if not bookmakers:
                    continue
                
                # Get first bookmaker
                bookmaker = bookmakers[0]
                bets = bookmaker.get('bets', [])
                
                for bet in bets:
                    bet_name = bet.get('name', '')
                    values = bet.get('values', [])
                    
                    # Match Winner (1X2)
                    if bet_name == 'Match Winner':
                        for value in values:
                            odd_type = value.get('value')
                            odd_value = float(value.get('odd', 2.0))
                            
                            if odd_type == 'Home':
                                match.home_odds = odd_value
                            elif odd_type == 'Draw':
                                match.draw_odds = odd_value
                            elif odd_type == 'Away':
                                match.away_odds = odd_value
                    
                    # Over/Under 2.5
                    elif bet_name == 'Goals Over/Under' and '2.5' in str(values):
                        for value in values:
                            if 'Over 2.5' in value.get('value', ''):
                                match.over25_odds = float(value.get('odd', 1.8))
                            elif 'Under 2.5' in value.get('value', ''):
                                match.under25_odds = float(value.get('odd', 2.0))
                    
                    # Both Teams to Score
                    elif bet_name == 'Both Teams Score':
                        for value in values:
                            odd_type = value.get('value')
                            odd_value = float(value.get('odd', 1.8))
                            
                            if odd_type == 'Yes':
                                match.gg_odds = odd_value
                            elif odd_type == 'No':
                                match.ng_odds = odd_value
                
                # Break after processing first bookmaker
                break
            
            match.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Updated odds for match {db_match_id}")
            return True
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating odds for match {db_match_id}: {e}")
            return False
    
    def _map_api_status_to_db_status(self, api_status):
        """Map API-Football status codes to our database status"""
        status_mapping = {
            'TBD': MatchStatus.SCHEDULED.value,
            'NS': MatchStatus.SCHEDULED.value,
            '1H': MatchStatus.LIVE.value,
            'HT': MatchStatus.LIVE.value,
            '2H': MatchStatus.LIVE.value,
            'ET': MatchStatus.LIVE.value,
            'P': MatchStatus.LIVE.value,
            'FT': MatchStatus.FINISHED.value,
            'AET': MatchStatus.FINISHED.value,
            'PEN': MatchStatus.FINISHED.value,
            'PST': MatchStatus.CANCELLED.value,
            'CANC': MatchStatus.CANCELLED.value,
            'ABD': MatchStatus.CANCELLED.value,
            'AWD': MatchStatus.FINISHED.value,
            'WO': MatchStatus.FINISHED.value
        }
        return status_mapping.get(api_status, MatchStatus.SCHEDULED.value)
    
    def get_popular_leagues(self):
        """Get list of popular league IDs for filtering"""
        return {
            'premier_league': 39,      # England - Premier League
            'la_liga': 140,            # Spain - La Liga
            'bundesliga': 78,          # Germany - Bundesliga
            'serie_a': 135,            # Italy - Serie A
            'ligue_1': 61,             # France - Ligue 1
            'champions_league': 2,     # UEFA Champions League
            'europa_league': 3,        # UEFA Europa League
            'world_cup': 1             # FIFA World Cup
        }


# Create global instance
football_api = FootballAPIService()
