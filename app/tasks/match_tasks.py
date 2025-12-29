"""
Background tasks for fetching live matches and updating odds
"""
from celery_app import celery
from app import create_app, db
from app.services.football_api import FootballAPIService, POPULAR_LEAGUES
from app.models.game_pick import GamePick
from app.models.ticket import Bet
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize Flask app context for Celery tasks
flask_app = create_app()

# Import WebSocket broadcast functions
try:
    from app.websocket_events import broadcast_match_update, broadcast_odds_update, broadcast_bet_settled
    WEBSOCKET_ENABLED = True
except ImportError:
    WEBSOCKET_ENABLED = False
    logger.warning("WebSocket events not available, real-time updates disabled")


@celery.task(name='app.tasks.match_tasks.fetch_live_matches')
def fetch_live_matches():
    """Fetch currently live matches from API and update database"""
    with flask_app.app_context():
        if not Config.FOOTBALL_API_ENABLED or not Config.FOOTBALL_API_KEY:
            logger.info("Football API not configured, skipping live match fetch")
            return {'status': 'skipped', 'reason': 'API not configured'}
        
        try:
            api = FootballAPIService(Config.FOOTBALL_API_KEY)
            
            # Fetch live matches for popular leagues
            all_live_matches = []
            for league_id in POPULAR_LEAGUES.values():
                matches = api.get_live_matches(league_id=league_id)
                all_live_matches.extend(matches)
            
            logger.info(f"Fetched {len(all_live_matches)} live matches")
            
            # Update database with live match data
            updated_count = 0
            for match_data in all_live_matches:
                game_pick = GamePick.query.filter_by(api_fixture_id=match_data['api_id']).first()
                
                if game_pick:
                    # Update existing match with live data
                    game_pick.home_score = match_data['home_score']
                    game_pick.away_score = match_data['away_score']
                    game_pick.status = match_data['status']
                    game_pick.elapsed_time = match_data['elapsed']
                    updated_count += 1
                    
                    # Broadcast real-time update via WebSocket
                    if WEBSOCKET_ENABLED:
                        broadcast_match_update(game_pick.to_dict())
            
            if updated_count > 0:
                db.session.commit()
                logger.info(f"Updated {updated_count} matches with live scores")
            
            return {
                'status': 'success',
                'fetched': len(all_live_matches),
                'updated': updated_count
            }
            
        except Exception as e:
            logger.error(f"Error fetching live matches: {e}")
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}


@celery.task(name='app.tasks.match_tasks.fetch_upcoming_matches')
def fetch_upcoming_matches():
    """Fetch upcoming matches for today and store in database"""
    with flask_app.app_context():
        if not Config.FOOTBALL_API_ENABLED or not Config.FOOTBALL_API_KEY:
            logger.info("Football API not configured, skipping upcoming match fetch")
            return {'status': 'skipped', 'reason': 'API not configured'}
        
        try:
            api = FootballAPIService(Config.FOOTBALL_API_KEY)
            
            # Fetch upcoming matches for popular leagues
            league_ids = list(POPULAR_LEAGUES.values())
            matches = api.get_upcoming_matches(league_ids=league_ids, limit=100)
            
            logger.info(f"Fetched {len(matches)} upcoming matches")
            
            # Store matches in database
            new_count = 0
            for match_data in matches:
                # Check if match already exists
                existing = GamePick.query.filter_by(api_fixture_id=match_data['api_id']).first()
                
                if not existing:
                    # Create new match
                    game_pick = GamePick(
                        match_name=f"{match_data['home_team']} vs {match_data['away_team']}",
                        league=match_data['league'],
                        api_fixture_id=match_data['api_id'],
                        api_league_id=match_data['league_id'],
                        home_team=match_data['home_team'],
                        away_team=match_data['away_team'],
                        kick_off_time=datetime.fromisoformat(match_data['kick_off'].replace('Z', '+00:00')),
                        status=match_data['status']
                    )
                    db.session.add(game_pick)
                    new_count += 1
            
            if new_count > 0:
                db.session.commit()
                logger.info(f"Added {new_count} new matches to database")
            
            return {
                'status': 'success',
                'fetched': len(matches),
                'added': new_count
            }
            
        except Exception as e:
            logger.error(f"Error fetching upcoming matches: {e}")
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}


@celery.task(name='app.tasks.match_tasks.update_match_odds')
def update_match_odds():
    """Update odds for upcoming and live matches"""
    with flask_app.app_context():
        if not Config.FOOTBALL_API_ENABLED or not Config.FOOTBALL_API_KEY:
            logger.info("Football API not configured, skipping odds update")
            return {'status': 'skipped', 'reason': 'API not configured'}
        
        try:
            api = FootballAPIService(Config.FOOTBALL_API_KEY)
            
            # Get matches that need odds updates (upcoming and live matches)
            matches = GamePick.query.filter(
                GamePick.status.in_(['NS', '1H', '2H', 'HT', 'LIVE'])
            ).limit(50).all()
            
            updated_count = 0
            for match in matches:
                if match.api_fixture_id:
                    odds_data = api.get_match_odds(match.api_fixture_id)
                    
                    if odds_data and odds_data.get('markets'):
                        # Update match odds from API
                        markets = odds_data['markets']
                        
                        # Update Match Winner (1X2) odds
                        if 'Match Winner' in markets:
                            winner_odds = markets['Match Winner']
                            match.odds_home = winner_odds.get('Home', 2.0)
                            match.odds_draw = winner_odds.get('Draw', 3.0)
                            match.odds_away = winner_odds.get('Away', 2.0)
                        
                        # Update Over/Under odds
                        if 'Goals Over/Under' in markets:
                            ou_odds = markets['Goals Over/Under']
                            match.odds_over_2_5 = ou_odds.get('Over 2.5', 1.8)
                            match.odds_under_2_5 = ou_odds.get('Under 2.5', 2.0)
                        
                        # Update Both Teams to Score
                        if 'Both Teams Score' in markets:
                            btts_odds = markets['Both Teams Score']
                            match.odds_btts_yes = btts_odds.get('Yes', 1.8)
                            match.odds_btts_no = btts_odds.get('No', 2.0)
                        
                        updated_count += 1
                        
                        # Broadcast odds update via WebSocket
                        if WEBSOCKET_ENABLED:
                            broadcast_odds_update(match.id, match.to_dict()['odds'])
            
            if updated_count > 0:
                db.session.commit()
                logger.info(f"Updated odds for {updated_count} matches")
            
            return {
                'status': 'success',
                'updated': updated_count
            }
            
        except Exception as e:
            logger.error(f"Error updating match odds: {e}")
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}


@celery.task(name='app.tasks.match_tasks.settle_finished_matches')
def settle_finished_matches():
    """Automatically settle bets for finished matches"""
    with flask_app.app_context():
        try:
            # Get matches that have finished
            finished_matches = GamePick.query.filter(
                GamePick.status == 'FT',
                GamePick.settled == False
            ).all()
            
            if not finished_matches:
                return {'status': 'success', 'settled': 0}
            
            settled_count = 0
            for match in finished_matches:
                # Get all pending bets for this match
                pending_bets = Bet.query.filter(
                    Bet.status == 'pending',
                    Bet.description.like(f'%{match.match_name}%')
                ).all()
                
                for bet in pending_bets:
                    # Determine if bet won or lost
                    result = determine_bet_result(bet, match)
                    
                    if result == 'won':
                        bet.status = 'won'
                        # Credit user account with winnings
                        bet.user.balance += bet.potential_payout
                        settled_count += 1
                        
                        # Notify user via WebSocket
                        if WEBSOCKET_ENABLED:
                            broadcast_bet_settled({
                                'bet_id': bet.id,
                                'user_id': bet.user_id,
                                'status': 'won',
                                'amount': bet.potential_payout
                            })
                    elif result == 'lost':
                        bet.status = 'lost'
                        settled_count += 1
                        
                        # Notify user via WebSocket
                        if WEBSOCKET_ENABLED:
                            broadcast_bet_settled({
                                'bet_id': bet.id,
                                'user_id': bet.user_id,
                                'status': 'lost',
                                'amount': 0
                            })
                    # If result is None, bet couldn't be determined (void scenario)
                
                # Mark match as settled
                match.settled = True
            
            if settled_count > 0:
                db.session.commit()
                logger.info(f"Settled {settled_count} bets for finished matches")
            
            return {
                'status': 'success',
                'settled': settled_count
            }
            
        except Exception as e:
            logger.error(f"Error settling finished matches: {e}")
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}


def determine_bet_result(bet: Bet, match: GamePick) -> str:
    """
    Determine if a bet won or lost based on match result
    
    Args:
        bet: The bet to evaluate
        match: The finished match
        
    Returns:
        'won', 'lost', or None if couldn't determine
    """
    try:
        home_score = match.home_score or 0
        away_score = match.away_score or 0
        total_goals = home_score + away_score
        
        # Parse bet description to get market and selection
        description = bet.description.lower()
        
        # Match Winner (1X2)
        if 'match winner' in description or 'full time result' in description:
            if 'home' in description:
                return 'won' if home_score > away_score else 'lost'
            elif 'draw' in description:
                return 'won' if home_score == away_score else 'lost'
            elif 'away' in description:
                return 'won' if away_score > home_score else 'lost'
        
        # Over/Under Goals
        if 'over' in description or 'under' in description:
            if 'over 2.5' in description:
                return 'won' if total_goals > 2.5 else 'lost'
            elif 'under 2.5' in description:
                return 'won' if total_goals < 2.5 else 'lost'
            elif 'over 1.5' in description:
                return 'won' if total_goals > 1.5 else 'lost'
            elif 'under 1.5' in description:
                return 'won' if total_goals < 1.5 else 'lost'
        
        # Both Teams to Score
        if 'both teams to score' in description or 'btts' in description:
            both_scored = home_score > 0 and away_score > 0
            if 'yes' in description:
                return 'won' if both_scored else 'lost'
            elif 'no' in description:
                return 'won' if not both_scored else 'lost'
        
        # Double Chance
        if 'double chance' in description:
            if 'home or draw' in description or '1x' in description:
                return 'won' if home_score >= away_score else 'lost'
            elif 'away or draw' in description or 'x2' in description:
                return 'won' if away_score >= home_score else 'lost'
            elif 'home or away' in description or '12' in description:
                return 'won' if home_score != away_score else 'lost'
        
        logger.warning(f"Could not determine result for bet {bet.id}: {description}")
        return None
        
    except Exception as e:
        logger.error(f"Error determining bet result: {e}")
        return None
