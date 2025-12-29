from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User
from app.models.virtual_game import VirtualLeague, VirtualTeam, VirtualGame, VirtualGameStatus
from app.services.virtual_game_service import VirtualGameService
from app.utils.decorators import token_required
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import random

logger = logging.getLogger(__name__)
virtual_game_bp = Blueprint('virtual_game', __name__, url_prefix='/api/virtual')
virtual_game_service = VirtualGameService()

# Admin check decorator
def admin_required(f):
    @token_required
    def wrapper(user, *args, **kwargs):
        if not getattr(user, 'is_admin', False):
            return jsonify({'message': 'Admin access required'}), 403
        return f(user, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ==================== PUBLIC ENDPOINTS ====================

@virtual_game_bp.route('/leagues', methods=['GET'])
def get_leagues():
    """Get all active virtual leagues"""
    try:
        leagues = virtual_game_service.get_active_leagues()
        return jsonify({
            'success': True,
            'leagues': [league.to_dict() for league in leagues]
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error fetching leagues: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/leagues/<int:league_id>/games', methods=['GET'])
def get_league_games(league_id):
    """Get games for a specific league"""
    try:
        status = request.args.get('status', 'scheduled')  # scheduled, live, finished
        
        if status == 'live':
            games = virtual_game_service.get_live_games(league_id)
        elif status == 'finished':
            games = virtual_game_service.get_finished_games(league_id, limit=20)
        else:
            games = virtual_game_service.get_upcoming_games(league_id, limit=20)
        
        return jsonify({
            'success': True,
            'games': [game.to_dict() for game in games]
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error fetching games: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/games/live', methods=['GET'])
def get_all_live_games():
    """Get all currently live games across all leagues"""
    try:
        games = virtual_game_service.get_live_games()
        return jsonify({
            'success': True,
            'games': [game.to_dict() for game in games]
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error fetching live games: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Get a specific game details"""
    try:
        game = VirtualGame.query.get(game_id)
        if not game:
            return jsonify({'success': False, 'message': 'Game not found'}), 404
        
        return jsonify({
            'success': True,
            'game': game.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error fetching game: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ADMIN ENDPOINTS ====================

# League Management
@virtual_game_bp.route('/admin/leagues', methods=['POST'])
@admin_required
def create_league(user):
    """Create a new virtual league"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        game_duration = data.get('game_duration', 180)
        games_per_day = data.get('games_per_day', 48)
        
        if not name:
            return jsonify({'success': False, 'message': 'League name required'}), 400
        
        league = virtual_game_service.create_league(
            name=name,
            description=description,
            game_duration=game_duration,
            games_per_day=games_per_day
        )
        
        logger.info(f"[VirtualGame] Admin {user.username} created league: {name}")
        
        return jsonify({
            'success': True,
            'message': 'League created successfully',
            'league': league.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"[VirtualGame] Error creating league: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues', methods=['GET'])
@admin_required
def get_all_leagues_admin(user):
    """Get all leagues (including inactive)"""
    try:
        leagues = virtual_game_service.get_all_leagues()
        return jsonify({
            'success': True,
            'leagues': [league.to_dict() for league in leagues]
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error fetching leagues: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>', methods=['PUT'])
@admin_required
def update_league(user, league_id):
    """Update league settings"""
    try:
        data = request.get_json()
        league = virtual_game_service.update_league(league_id, **data)
        
        logger.info(f"[VirtualGame] Admin {user.username} updated league {league_id}")
        
        return jsonify({
            'success': True,
            'message': 'League updated successfully',
            'league': league.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error updating league: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>', methods=['DELETE'])
@admin_required
def delete_league(user, league_id):
    """Delete a league"""
    try:
        virtual_game_service.delete_league(league_id)
        
        logger.info(f"[VirtualGame] Admin {user.username} deleted league {league_id}")
        
        return jsonify({
            'success': True,
            'message': 'League deleted successfully'
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error deleting league: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Team Management
@virtual_game_bp.route('/admin/leagues/<int:league_id>/teams', methods=['POST'])
@admin_required
def create_team(user, league_id):
    """Create a new team in a league"""
    try:
        data = request.get_json()
        name = data.get('name')
        rating = data.get('rating', 75)
        
        if not name:
            return jsonify({'success': False, 'message': 'Team name required'}), 400
        
        team = virtual_game_service.create_team(
            league_id=league_id,
            name=name,
            rating=rating
        )
        
        logger.info(f"[VirtualGame] Admin {user.username} created team: {name}")
        
        return jsonify({
            'success': True,
            'message': 'Team created successfully',
            'team': team.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"[VirtualGame] Error creating team: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>/teams', methods=['GET'])
@admin_required
def get_league_teams(user, league_id):
    """Get all teams in a league"""
    try:
        teams = virtual_game_service.get_league_teams(league_id)
        return jsonify({
            'success': True,
            'teams': [team.to_dict() for team in teams]
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error fetching teams: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/teams/<int:team_id>', methods=['PUT'])
@admin_required
def update_team(user, team_id):
    """Update team details"""
    try:
        data = request.get_json()
        team = virtual_game_service.update_team(team_id, **data)
        
        logger.info(f"[VirtualGame] Admin {user.username} updated team {team_id}")
        
        return jsonify({
            'success': True,
            'message': 'Team updated successfully',
            'team': team.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error updating team: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/teams/<int:team_id>', methods=['DELETE'])
@admin_required
def delete_team(user, team_id):
    """Delete a team"""
    try:
        virtual_game_service.delete_team(team_id)
        
        logger.info(f"[VirtualGame] Admin {user.username} deleted team {team_id}")
        
        return jsonify({
            'success': True,
            'message': 'Team deleted successfully'
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error deleting team: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Game Management
@virtual_game_bp.route('/admin/games', methods=['GET'])
@admin_required
def get_all_games(user):
    """Get all virtual games (admin)"""
    try:
        games = VirtualGame.query.order_by(VirtualGame.scheduled_start.desc()).limit(100).all()
        return jsonify({
            'success': True,
            'games': [game.to_dict() for game in games]
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error fetching all games: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/leagues/<int:league_id>/race-info', methods=['GET'])
def get_league_race_info(league_id):
    """Get current race information for a league - NO AUTH for frontend access"""
    try:
        league = VirtualLeague.query.get(league_id)
        if not league:
            return jsonify({'success': False, 'message': 'League not found'}), 404
        
        # Count finished games to determine current race
        finished_count = VirtualGame.query.filter_by(
            league_id=league_id,
            status=VirtualGameStatus.FINISHED.value
        ).count()
        
        # Each race has 10 games, so race_number = (finished_count // 10) + 1
        current_race = (finished_count // 10) + 1
        # Season lasts 38 races, then resets
        current_season = ((current_race - 1) // 38) + 1
        race_in_season = ((current_race - 1) % 38) + 1
        
        # Get scheduled games count
        scheduled_count = VirtualGame.query.filter_by(
            league_id=league_id,
            status=VirtualGameStatus.SCHEDULED.value
        ).count()
        
        # Get LIVE games and calculate current phase based on server time
        live_games = VirtualGame.query.filter_by(
            league_id=league_id,
            status=VirtualGameStatus.LIVE.value
        ).all()
        
        current_phase = 'countdown'  # Default phase
        seconds_remaining = 180  # Default 3 minutes countdown
        play_time = 0
        
        if live_games:
            # If there are live games, we're in playing phase
            # Calculate elapsed time from the first live game's actual_start
            first_live = live_games[0]
            if first_live.actual_start:
                elapsed = (datetime.utcnow() - first_live.actual_start).total_seconds()
                if elapsed < first_live.game_duration:
                    current_phase = 'playing'
                    play_time = int(elapsed)
                    seconds_remaining = first_live.game_duration - play_time
                else:
                    # Game should have finished, might be in buffer
                    current_phase = 'buffer'
                    buffer_elapsed = int(elapsed - first_live.game_duration)
                    seconds_remaining = max(0, 30 - buffer_elapsed)  # 30 sec buffer
        elif scheduled_count > 0:
            # We have scheduled games, check their scheduled_start time
            next_game = VirtualGame.query.filter_by(
                league_id=league_id,
                status=VirtualGameStatus.SCHEDULED.value
            ).order_by(VirtualGame.scheduled_start).first()
            
            if next_game and next_game.scheduled_start:
                time_until_start = (next_game.scheduled_start - datetime.utcnow()).total_seconds()
                if time_until_start > 0:
                    current_phase = 'countdown'
                    seconds_remaining = int(time_until_start)
                else:
                    # Scheduled time passed but not started yet, start now
                    current_phase = 'countdown'
                    seconds_remaining = 0
        
        return jsonify({
            'success': True,
            'race_number': race_in_season,
            'season_number': current_season,
            'finished_games': finished_count,
            'scheduled_games': scheduled_count,
            'live_games': len(live_games),
            'total_races': 38,
            'current_phase': current_phase,  # 'countdown', 'playing', or 'buffer'
            'seconds_remaining': seconds_remaining,
            'play_time': play_time,
            'server_time': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error getting race info: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/leagues/<int:league_id>/standings', methods=['GET'])
def get_league_standings(league_id):
    """Get league standings table calculated from ALL finished games in database"""
    try:
        from sqlalchemy import func
        
        # Get all finished games for this league from database
        finished_games = VirtualGame.query.filter_by(
            league_id=league_id,
            status=VirtualGameStatus.FINISHED.value
        ).all()
        
        logger.info(f"[VirtualStandings] ==========================================")
        logger.info(f"[VirtualStandings] League {league_id}: Found {len(finished_games)} finished games in database")
        
        if len(finished_games) > 0:
            logger.info(f"[VirtualStandings] Sample games: {[(g.id, g.home_score, g.away_score, g.status) for g in finished_games[:3]]}")
        
        # Get all teams in the league
        teams_data = {}
        all_teams = VirtualTeam.query.filter_by(league_id=league_id).all()
        
        # Initialize all teams with 0 stats
        for team in all_teams:
            teams_data[team.name] = {
                'name': team.name,
                'played': 0,
                'won': 0,
                'drawn': 0,
                'lost': 0,
                'gf': 0,
                'ga': 0,
                'pts': 0
            }
        
        # Calculate stats from finished games
        for game in finished_games:
            # Get team names safely
            home_team = game.home_team.name if game.home_team else game.to_dict()['home_team']
            away_team = game.away_team.name if game.away_team else game.to_dict()['away_team']
            
            # Ensure teams exist in dict
            if home_team not in teams_data:
                teams_data[home_team] = {'name': home_team, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0, 'gf': 0, 'ga': 0, 'pts': 0}
            if away_team not in teams_data:
                teams_data[away_team] = {'name': away_team, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0, 'gf': 0, 'ga': 0, 'pts': 0}
            
            teams_data[home_team]['played'] += 1
            teams_data[away_team]['played'] += 1
            teams_data[home_team]['gf'] += game.home_score or 0
            teams_data[home_team]['ga'] += game.away_score or 0
            teams_data[away_team]['gf'] += game.away_score or 0
            teams_data[away_team]['ga'] += game.home_score or 0
            
            if game.home_score > game.away_score:
                teams_data[home_team]['won'] += 1
                teams_data[home_team]['pts'] += 3
                teams_data[away_team]['lost'] += 1
            elif game.home_score < game.away_score:
                teams_data[away_team]['won'] += 1
                teams_data[away_team]['pts'] += 3
                teams_data[home_team]['lost'] += 1
            else:
                teams_data[home_team]['drawn'] += 1
                teams_data[away_team]['drawn'] += 1
                teams_data[home_team]['pts'] += 1
                teams_data[away_team]['pts'] += 1
        
        # Sort standings
        standings = sorted(teams_data.values(), key=lambda x: (
            -x['pts'],  # Points descending
            -(x['gf'] - x['ga']),  # Goal difference descending
            -x['gf'],  # Goals for descending
            x['name']  # Name ascending (alphabetical tiebreaker)
        ))
        
        # If no games played yet, sort alphabetically
        if not finished_games:
            standings = sorted(standings, key=lambda x: x['name'])
        
        logger.info(f"[VirtualGame] Calculated standings for league {league_id}: {len(standings)} teams, {len(finished_games)} games")
        
        return jsonify({
            'success': True,
            'standings': standings,
            'games_played': len(finished_games)
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error calculating standings: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/bets/place', methods=['POST'])
@jwt_required()
def place_virtual_bet():
    """Place a bet on virtual games"""
    try:
        from app.models import Bet
        
        user = User.query.get(get_jwt_identity())
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        data = request.get_json()
        amount = float(data.get('amount', 0))
        selections = data.get('selections', [])
        
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid bet amount'}), 400
        
        if not selections:
            return jsonify({'success': False, 'message': 'No selections provided'}), 400
        
        # Check user balance
        if user.balance < amount:
            return jsonify({'success': False, 'message': 'Insufficient balance'}), 400
        
        # Calculate total odds
        total_odds = 1.0
        for sel in selections:
            total_odds *= float(sel.get('odd', 1))
        
        potential_win = amount * total_odds
        
        # Create bet record using regular Bet model
        # Store selections as JSON in a text field
        import json
        
        # Get league info for bet description
        first_game = VirtualGame.query.get(selections[0]['game_id']) if selections else None
        league = VirtualLeague.query.get(first_game.league_id) if first_game else None
        league_name = league.name if league else 'Virtual'
        
        # Build event description with bet details
        selections_summary = []
        for sel in selections:
            game = VirtualGame.query.get(sel['game_id'])
            if game:
                home_name = game.home_team.name if game.home_team else 'Unknown'
                away_name = game.away_team.name if game.away_team else 'Unknown'
                selections_summary.append(f"{home_name} vs {away_name} - {sel.get('market', '1X2')}: {sel.get('selection', '')} @ {sel.get('odd', 0)}")
        
        event_desc = f"{league_name} - Virtual Multi-Bet ({len(selections)} selections)\n" + "\n".join(selections_summary)
        
        try:
            # Store selections as JSON for auto-settlement
            bet = Bet(
                user_id=user.id,
                amount=amount,
                potential_payout=potential_win,
                odds=total_odds,
                status='pending',
                bet_type='virtual',  # Mark as virtual for auto-settlement
                event_description=event_desc,
                selection=json.dumps(selections)  # Store selections with game_id, market, selection, odd
            )
            
            # Deduct from balance
            user.balance -= amount
            
            db.session.add(bet)
            db.session.commit()
            
            logger.info(f"[VirtualBet] Created virtual bet ID {bet.id} for user {user.username}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualBet] Error creating bet: {str(e)}")
            return jsonify({'success': False, 'message': f'Error placing bet: {str(e)}'}), 500
        
        logger.info(f"[VirtualBet] User {user.username} placed virtual bet: ${amount}, odds: {total_odds:.2f}")
        
        return jsonify({
            'success': True,
            'message': f'Bet placed successfully! Potential win: ${potential_win:.2f}',
            'bet_id': bet.id,
            'new_balance': float(user.balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"[VirtualBet] Error placing bet: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/games', methods=['POST'])
@admin_required
def create_game(user):
    """Create a new virtual game"""
    try:
        data = request.get_json()
        league_id = data.get('league_id')
        home_team_id = data.get('home_team_id')
        away_team_id = data.get('away_team_id')
        scheduled_start = data.get('scheduled_start')
        auto_play = data.get('auto_play', True)
        
        if not all([league_id, home_team_id, away_team_id, scheduled_start]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Parse scheduled start time
        scheduled_dt = datetime.fromisoformat(scheduled_start.replace('Z', '+00:00'))
        
        game = virtual_game_service.create_game(
            league_id=league_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            scheduled_start=scheduled_dt,
            auto_play=auto_play
        )
        
        logger.info(f"[VirtualGame] Admin {user.username} created game {game.id}")
        
        return jsonify({
            'success': True,
            'message': 'Game created successfully',
            'game': game.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"[VirtualGame] Error creating game: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>/schedule-games', methods=['POST'])
@admin_required
def schedule_league_games(user, league_id):
    """Schedule multiple games for a league"""
    try:
        data = request.get_json()
        num_games = data.get('num_games', 10)
        start_time = data.get('start_time')
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = datetime.utcnow()
        
        games = virtual_game_service.schedule_games_for_league(
            league_id=league_id,
            num_games=num_games,
            start_time=start_dt
        )
        
        logger.info(f"[VirtualGame] Admin {user.username} scheduled {len(games)} games for league {league_id}")
        
        return jsonify({
            'success': True,
            'message': f'Scheduled {len(games)} games',
            'games': [game.to_dict() for game in games]
        }), 201
    except Exception as e:
        logger.error(f"[VirtualGame] Error scheduling games: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>/generate-games', methods=['POST'])
def generate_league_games(league_id):
    """Generate games for a league (10 matches for 20-team format) - Auto-called by frontend"""
    try:
        data = request.get_json() or {}
        num_games = data.get('num_games', 10)  # Default 10 matches per race
        
        # Clean up ONLY scheduled games (keep finished games for standings history)
        old_scheduled = VirtualGame.query.filter_by(
            league_id=league_id,
            status=VirtualGameStatus.SCHEDULED.value
        ).all()
        
        for game in old_scheduled:
            db.session.delete(game)
        
        if old_scheduled:
            db.session.commit()
            logger.info(f"[VirtualGame] Cleaned up {len(old_scheduled)} scheduled games for league {league_id}")
        
        # Count total finished games for history tracking
        finished_count = VirtualGame.query.filter_by(
            league_id=league_id,
            status=VirtualGameStatus.FINISHED.value
        ).count()
        logger.info(f"[VirtualGame] League {league_id} has {finished_count} finished games in history")
        
        # Pass None so service will set start_time = now + 180 seconds (countdown)
        games = virtual_game_service.schedule_games_for_league(
            league_id=league_id,
            num_games=num_games,
            start_time=None  # Service will add 180 second countdown
        )
        
        logger.info(f"[VirtualGame] Auto-generated {len(games)} games for league {league_id}, starting in 180 seconds")
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(games)} games',
            'games': [game.to_dict() for game in games],
            'scheduled_start': games[0].scheduled_start.isoformat() if games else None
        }), 201
    except Exception as e:
        logger.error(f"[VirtualGame] Error generating games: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/games/<int:game_id>/start', methods=['POST'])
@admin_required
def start_game(user, game_id):
    """Start a virtual game"""
    try:
        game = virtual_game_service.start_game(game_id)
        
        logger.info(f"[VirtualGame] Admin {user.username} started game {game_id}")
        
        return jsonify({
            'success': True,
            'message': 'Game started',
            'game': game.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error starting game: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/games/<int:game_id>/update-score', methods=['POST'])
@admin_required
def update_score(user, game_id):
    """Update game score (admin control)"""
    try:
        data = request.get_json()
        home_score = data.get('home_score', 0)
        away_score = data.get('away_score', 0)
        current_minute = data.get('current_minute')
        
        game = virtual_game_service.update_game_score(
            game_id=game_id,
            home_score=home_score,
            away_score=away_score,
            current_minute=current_minute
        )
        
        logger.info(f"[VirtualGame] Admin {user.username} updated game {game_id} score: {home_score}-{away_score}")
        
        return jsonify({
            'success': True,
            'message': 'Score updated',
            'game': game.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error updating score: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/games/<int:game_id>/finish', methods=['POST'])
def finish_game(game_id):
    """Finish a virtual game - Auto-called by frontend"""
    try:
        data = request.get_json() or {}
        home_score = data.get('home_score', 0)
        away_score = data.get('away_score', 0)
        
        # Update game scores before finishing
        game = VirtualGame.query.get(game_id)
        if not game:
            return jsonify({'success': False, 'message': 'Game not found'}), 404
        
        game.home_score = home_score
        game.away_score = away_score
        game.status = VirtualGameStatus.FINISHED.value  # Use .value to get string 'finished'
        db.session.commit()
        
        logger.info(f"[VirtualGame] ✅ Game {game_id} saved to DB: {home_score}-{away_score}, status={game.status}")
        
        # Verify it's actually in the database
        check_game = VirtualGame.query.get(game_id)
        logger.info(f"[VirtualGame] Verification: Game {game_id} status in DB = {check_game.status if check_game else 'NOT FOUND'}")
        
        # Count total finished games for this league
        total_finished = VirtualGame.query.filter_by(
            league_id=game.league_id,
            status=VirtualGameStatus.FINISHED.value
        ).count()
        logger.info(f"[VirtualGame] League {game.league_id} now has {total_finished} finished games in database")
        
        # Settle ALL pending virtual bets (not just for this game)
        virtual_game_service.settle_all_virtual_bets()
        
        logger.info(f"[VirtualGame] Game {game_id} finished automatically: {home_score}-{away_score}")
        
        return jsonify({
            'success': True,
            'message': 'Game finished and bets settled',
            'game': game.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error finishing game: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/games/<int:game_id>/simulate', methods=['POST'])
@admin_required
def simulate_game(user, game_id):
    """Auto-simulate a game result"""
    try:
        game = virtual_game_service.simulate_game_auto(game_id)
        
        logger.info(f"[VirtualGame] Admin {user.username} simulated game {game_id}")
        
        return jsonify({
            'success': True,
            'message': 'Game simulated and finished',
            'game': game.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error simulating game: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/games/<int:game_id>', methods=['DELETE'])
@admin_required
def delete_game(user, game_id):
    """Delete a game"""
    try:
        virtual_game_service.delete_game(game_id)
        
        logger.info(f"[VirtualGame] Admin {user.username} deleted game {game_id}")
        
        return jsonify({
            'success': True,
            'message': 'Game deleted successfully'
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error deleting game: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Reset All Leagues to MD1
@virtual_game_bp.route('/admin/reset-all-leagues', methods=['POST'])
@admin_required
def reset_all_leagues(user):
    """Reset all leagues to Matchday 1 - Clear ALL games (finished and scheduled)"""
    try:
        # Delete ALL games (both finished AND scheduled) from all leagues
        all_games = VirtualGame.query.all()
        total_deleted = len(all_games)
        
        for game in all_games:
            db.session.delete(game)
        
        db.session.commit()
        
        logger.info(f"[VirtualGame] Admin {user.username} reset all leagues - deleted {total_deleted} total games (finished + scheduled)")
        
        return jsonify({
            'success': True,
            'message': f'Reset complete! Deleted {total_deleted} games. All leagues back to MD1.',
            'games_deleted': total_deleted
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[VirtualGame] Error resetting leagues: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Quick Setup Endpoint
@virtual_game_bp.route('/admin/quick-setup', methods=['POST'])
@admin_required
def quick_setup(user):
    """Quick setup: Create 3 leagues with teams and schedule games"""
    try:
        data = request.get_json() or {}  # Handle empty body
        
        # Check if ANY leagues exist - delete them first
        existing_count = VirtualLeague.query.count()
        
        if existing_count > 0:
            logger.info(f"[VirtualGame] Quick Setup: Deleting {existing_count} existing leagues first")
            # Delete all existing leagues (cascade will handle teams and games)
            VirtualLeague.query.delete()
            db.session.commit()
            logger.info(f"[VirtualGame] Quick Setup: Deleted all existing data")
        
        # Real league configurations with 20 teams each
        league_configs = [
            {
                'name': 'Premier League',
                'description': 'English Premier League',
                'teams': ['Man City', 'Arsenal', 'Liverpool', 'Aston Villa', 'Tottenham', 'Chelsea', 'Newcastle', 'Man United', 'West Ham', 'Brighton', 
                         'Crystal Palace', 'Fulham', 'Brentford', 'Everton', 'Nottingham', 'Wolves', 'Bournemouth', 'Luton Town', 'Burnley', 'Sheffield Utd']
            },
            {
                'name': 'La Liga',
                'description': 'Spanish La Liga',
                'teams': ['Real Madrid', 'Barcelona', 'Girona', 'Atletico Madrid', 'Athletic Bilbao', 'Real Sociedad', 'Real Betis', 'Valencia', 'Villarreal', 'Getafe',
                         'Sevilla', 'Osasuna', 'Las Palmas', 'Celta Vigo', 'Rayo Vallecano', 'Mallorca', 'Alaves', 'Cadiz', 'Granada', 'Almeria']
            },
            {
                'name': 'Serie A',
                'description': 'Italian Serie A',
                'teams': ['Inter Milan', 'AC Milan', 'Juventus', 'Atalanta', 'Bologna', 'Roma', 'Napoli', 'Lazio', 'Fiorentina', 'Torino',
                         'Frosinone', 'Verona', 'Monza', 'Genoa', 'Lecce', 'Udinese', 'Cagliari', 'Empoli', 'Sassuolo', 'Salernitana']
            }
        ]
        
        created_leagues = []
        
        for config in league_configs:
            # Create league
            league = virtual_game_service.create_league(
                name=config['name'],
                description=config['description'],
                game_duration=180,
                games_per_day=48
            )
            
            # Create teams
            for team_name in config['teams']:
                rating = random.randint(70, 95)
                virtual_game_service.create_team(
                    league_id=league.id,
                    name=team_name,
                    rating=rating
                )
            
            # Schedule games (10 matches for 20-team format)
            games = virtual_game_service.schedule_games_for_league(
                league_id=league.id,
                num_games=10,
                start_time=datetime.utcnow()
            )
            
            created_leagues.append({
                'league': league.to_dict(),
                'teams_count': len(config['teams']),
                'games_scheduled': len(games)
            })
        
        # Calculate totals
        total_teams = sum([item['teams_count'] for item in created_leagues])
        total_games = sum([item['games_scheduled'] for item in created_leagues])
        
        logger.info(f"[VirtualGame] Admin {user.username} ran quick setup")
        
        return jsonify({
            'success': True,
            'message': 'Quick setup completed',
            'leagues_created': len(created_leagues),
            'teams_created': total_teams,
            'games_created': total_games,
            'leagues': created_leagues
        }), 201
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"[VirtualGame] Error in quick setup: {e}\n{error_details}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'details': error_details if __debug__ else None
        }), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>/race-info', methods=['GET'])
@admin_required
def get_race_info(user, league_id):
    """Get race/season information for a league"""
    try:
        from sqlalchemy import func
        
        # Get total games
        total_games = db.session.query(func.count(VirtualGame.id)).filter_by(league_id=league_id).scalar() or 0
        
        # Get scheduled games
        scheduled = db.session.query(func.count(VirtualGame.id)).filter_by(
            league_id=league_id, 
            status=VirtualGameStatus.SCHEDULED.value
        ).scalar() or 0
        
        # Get live games
        live = db.session.query(func.count(VirtualGame.id)).filter_by(
            league_id=league_id,
            status=VirtualGameStatus.LIVE.value
        ).scalar() or 0
        
        # Get finished games
        finished = db.session.query(func.count(VirtualGame.id)).filter_by(
            league_id=league_id,
            status=VirtualGameStatus.FINISHED.value
        ).scalar() or 0
        
        # Calculate current race/matchday (assuming 10 matches per race)
        current_race = (scheduled // 10) + 1 if scheduled > 0 else 0
        current_season = ((finished // 10) // 38) + 1
        current_matchday = ((finished // 10) % 38) + 1
        
        return jsonify({
            'success': True,
            'league_id': league_id,
            'total_games': total_games,
            'scheduled': scheduled,
            'live': live,
            'finished': finished,
            'current_race': current_race,
            'current_season': current_season,
            'current_matchday': current_matchday,
            'races_per_season': 38,
            'matches_per_race': 10
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error getting race info: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>/clear-games', methods=['POST'])
@jwt_required()
def clear_league_games(league_id):
    """Clear all games for a specific league"""
    try:
        user = User.query.get(get_jwt_identity())
        if not user or not user.is_admin:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        games_deleted = virtual_game_service.clear_all_games(league_id)
        
        logger.info(f"[VirtualGame] Admin {user.username} cleared {games_deleted} games from league {league_id}")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {games_deleted} games',
            'games_deleted': games_deleted
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error clearing games: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/leagues/<int:league_id>/reset', methods=['POST'])
@jwt_required()
def reset_league(league_id):
    """Reset a league - clear all games and prepare for fresh start"""
    try:
        user = User.query.get(get_jwt_identity())
        if not user or not user.is_admin:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        result = virtual_game_service.reset_league(league_id)
        
        logger.info(f"[VirtualGame] Admin {user.username} reset league {league_id}")
        
        return jsonify({
            'success': True,
            'message': f'League reset: {result["games_deleted"]} games deleted',
            'games_deleted': result['games_deleted'],
            'teams_count': result['teams_count']
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error resetting league: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/clear-all-games', methods=['POST'])
@jwt_required()
def clear_all_virtual_games():
    """Clear all virtual games across all leagues"""
    try:
        user = User.query.get(get_jwt_identity())
        if not user or not user.is_admin:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        games_deleted = virtual_game_service.clear_all_games()
        
        logger.info(f"[VirtualGame] Admin {user.username} cleared ALL {games_deleted} virtual games")
        
        return jsonify({
            'success': True,
            'message': f'Cleared all {games_deleted} games from all leagues',
            'games_deleted': games_deleted
        }), 200
    except Exception as e:
        logger.error(f"[VirtualGame] Error clearing all games: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@virtual_game_bp.route('/admin/delete-all-leagues', methods=['POST'])
@admin_required
def delete_all_leagues(user):
    """Delete all virtual leagues, teams, and games - complete reset"""
    try:
        
        # Get counts before deletion
        leagues_count = VirtualLeague.query.count()
        teams_count = VirtualTeam.query.count()
        games_count = VirtualGame.query.count()
        
        # Delete all (cascade will handle teams and games)
        VirtualLeague.query.delete()
        db.session.commit()
        
        logger.info(f"[VirtualGame] Admin {user.username} deleted ALL virtual data: {leagues_count} leagues, {teams_count} teams, {games_count} games")
        
        return jsonify({
            'success': True,
            'message': f'Deleted everything: {leagues_count} leagues, {teams_count} teams, {games_count} games',
            'leagues_deleted': leagues_count,
            'teams_deleted': teams_count,
            'games_deleted': games_count
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"[VirtualGame] Error deleting all leagues: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
