"""
Football API Integration Service
Integrates with API-Football (RapidAPI) for live match data and odds
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FootballAPIService:
    """Service for fetching live football match data and odds from API-Football"""
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self, api_key: str):
        """
        Initialize Football API service
        
        Args:
            api_key: API-Football API key
        """
        self.api_key = api_key
        self.headers = {
            'x-apisports-key': self.api_key
        }
    
    def get_live_matches(self, league_id: Optional[int] = None) -> List[Dict]:
        """
        Get currently live matches
        
        Args:
            league_id: Optional league ID to filter by
            
        Returns:
            List of live match dictionaries
        """
        try:
            endpoint = f"{self.BASE_URL}/fixtures"
            params = {'live': 'all'}
            
            if league_id:
                params['league'] = league_id
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response'):
                logger.info(f"Fetched {len(data['response'])} live matches")
                return self._parse_fixtures(data['response'])
            return []
            
        except requests.RequestException as e:
            logger.error(f"Error fetching live matches: {e}")
            return []
    
    def get_upcoming_matches(self, date: str = None, league_ids: List[int] = None, limit: int = 50) -> List[Dict]:
        """
        Get upcoming matches for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            league_ids: List of league IDs to fetch
            limit: Maximum number of matches to return
            
        Returns:
            List of upcoming match dictionaries
        """
        try:
            endpoint = f"{self.BASE_URL}/fixtures"
            
            if date is None:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            params = {'date': date}
            
            all_matches = []
            
            if league_ids:
                # Fetch for each league separately to ensure we get matches
                for league_id in league_ids:
                    params['league'] = league_id
                    response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get('response'):
                        all_matches.extend(data['response'])
            else:
                # Fetch all matches for the date
                response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get('response'):
                    all_matches = data['response']
            
            logger.info(f"Fetched {len(all_matches)} upcoming matches for {date}")
            return self._parse_fixtures(all_matches[:limit])
            
        except requests.RequestException as e:
            logger.error(f"Error fetching upcoming matches: {e}")
            return []
    
    def get_match_odds(self, fixture_id: int, bookmaker_id: int = 8) -> Dict:
        """
        Get betting odds for a specific match
        
        Args:
            fixture_id: API-Football fixture ID
            bookmaker_id: Bookmaker ID (default: 8 = Bet365)
            
        Returns:
            Dictionary containing odds data
        """
        try:
            endpoint = f"{self.BASE_URL}/odds"
            params = {
                'fixture': fixture_id,
                'bookmaker': bookmaker_id
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response') and len(data['response']) > 0:
                return self._parse_odds(data['response'][0])
            return {}
            
        except requests.RequestException as e:
            logger.error(f"Error fetching odds for fixture {fixture_id}: {e}")
            return {}
    
    def get_leagues(self, country: str = None) -> List[Dict]:
        """
        Get available leagues
        
        Args:
            country: Optional country name to filter by
            
        Returns:
            List of league dictionaries
        """
        try:
            endpoint = f"{self.BASE_URL}/leagues"
            params = {}
            
            if country:
                params['country'] = country
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response'):
                return [{
                    'id': league['league']['id'],
                    'name': league['league']['name'],
                    'country': league['country']['name'],
                    'logo': league['league']['logo'],
                    'season': league['seasons'][-1]['year'] if league['seasons'] else None
                } for league in data['response']]
            return []
            
        except requests.RequestException as e:
            logger.error(f"Error fetching leagues: {e}")
            return []
    
    def _parse_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Parse API fixtures into our format"""
        parsed = []
        
        for fixture in fixtures:
            try:
                parsed.append({
                    'api_id': fixture['fixture']['id'],
                    'league': fixture['league']['name'],
                    'league_id': fixture['league']['id'],
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'home_logo': fixture['teams']['home']['logo'],
                    'away_logo': fixture['teams']['away']['logo'],
                    'kick_off': fixture['fixture']['date'],
                    'status': fixture['fixture']['status']['short'],
                    'elapsed': fixture['fixture']['status']['elapsed'],
                    'home_score': fixture['goals']['home'],
                    'away_score': fixture['goals']['away'],
                    'venue': fixture['fixture']['venue']['name'] if fixture['fixture']['venue'] else None
                })
            except (KeyError, TypeError) as e:
                logger.warning(f"Error parsing fixture: {e}")
                continue
        
        return parsed
    
    def _parse_odds(self, odds_data: Dict) -> Dict:
        """Parse API odds into our format"""
        try:
            fixture = odds_data['fixture']
            league = odds_data['league']
            bookmaker = odds_data['bookmakers'][0] if odds_data.get('bookmakers') else None
            
            result = {
                'fixture_id': fixture['id'],
                'league_name': league['name'],
                'markets': {}
            }
            
            if bookmaker and bookmaker.get('bets'):
                for bet in bookmaker['bets']:
                    market_name = bet['name']
                    values = {}
                    
                    for value in bet.get('values', []):
                        values[value['value']] = float(value['odd'])
                    
                    result['markets'][market_name] = values
            
            return result
            
        except (KeyError, TypeError, IndexError) as e:
            logger.warning(f"Error parsing odds: {e}")
            return {}


# Popular league IDs for quick reference
POPULAR_LEAGUES = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61,
    'Champions League': 2,
    'Europa League': 3,
    'World Cup': 1
}
