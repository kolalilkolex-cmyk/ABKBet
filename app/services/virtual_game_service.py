import random
import json
from datetime import datetime, timedelta
from app.extensions import db
from app.models.virtual_game import VirtualLeague, VirtualTeam, VirtualGame, VirtualGameStatus
import logging

logger = logging.getLogger(__name__)

class VirtualGameService:
    """Service for managing virtual games"""
    
    def __init__(self):
        pass
    
    # ================== League Management ==================
    
    def create_league(self, name, description=None, game_duration=180, games_per_day=48):
        """Create a new virtual league"""
        try:
            league = VirtualLeague(
                name=name,
                description=description,
                game_duration_seconds=game_duration,
                games_per_day=games_per_day,
                is_active=True
            )
            db.session.add(league)
            db.session.commit()
            logger.info(f"[VirtualGame] Created league: {name}")
            return league
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error creating league: {e}")
            raise
    
    def get_all_leagues(self):
        """Get all virtual leagues"""
        return VirtualLeague.query.all()
    
    def get_active_leagues(self):
        """Get only active leagues"""
        return VirtualLeague.query.filter_by(is_active=True).all()
    
    def update_league(self, league_id, **kwargs):
        """Update league settings"""
        try:
            league = VirtualLeague.query.get(league_id)
            if not league:
                raise ValueError("League not found")
            
            for key, value in kwargs.items():
                if hasattr(league, key):
                    setattr(league, key, value)
            
            db.session.commit()
            logger.info(f"[VirtualGame] Updated league {league_id}")
            return league
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error updating league: {e}")
            raise
    
    def delete_league(self, league_id):
        """Delete a league and all its teams/games"""
        try:
            league = VirtualLeague.query.get(league_id)
            if not league:
                raise ValueError("League not found")
            
            db.session.delete(league)
            db.session.commit()
            logger.info(f"[VirtualGame] Deleted league {league_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error deleting league: {e}")
            raise
    
    # ================== Team Management ==================
    
    def create_team(self, league_id, name, rating=75):
        """Create a new team in a league"""
        try:
            league = VirtualLeague.query.get(league_id)
            if not league:
                raise ValueError("League not found")
            
            team = VirtualTeam(
                league_id=league_id,
                name=name,
                rating=rating
            )
            db.session.add(team)
            db.session.commit()
            logger.info(f"[VirtualGame] Created team: {name} in league {league_id}")
            return team
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error creating team: {e}")
            raise
    
    def get_league_teams(self, league_id):
        """Get all teams in a league"""
        return VirtualTeam.query.filter_by(league_id=league_id).all()
    
    def update_team(self, team_id, **kwargs):
        """Update team details"""
        try:
            team = VirtualTeam.query.get(team_id)
            if not team:
                raise ValueError("Team not found")
            
            for key, value in kwargs.items():
                if hasattr(team, key):
                    setattr(team, key, value)
            
            db.session.commit()
            logger.info(f"[VirtualGame] Updated team {team_id}")
            return team
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error updating team: {e}")
            raise
    
    def delete_team(self, team_id):
        """Delete a team"""
        try:
            team = VirtualTeam.query.get(team_id)
            if not team:
                raise ValueError("Team not found")
            
            db.session.delete(team)
            db.session.commit()
            logger.info(f"[VirtualGame] Deleted team {team_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error deleting team: {e}")
            raise
    
    # ================== Game Generation ==================
    
    def generate_odds(self, home_rating, away_rating):
        """Generate realistic odds based on team ratings"""
        rating_diff = home_rating - away_rating
        
        # Base odds calculation (FIXED: big rating_diff means home is favorite = LOW odds)
        if rating_diff > 20:  # Home much stronger
            home_odds = round(random.uniform(1.20, 1.45), 2)  # Favorite gets LOW odds
            draw_odds = round(random.uniform(5.00, 6.50), 2)
            away_odds = round(random.uniform(8.00, 15.00), 2)  # Underdog gets HIGH odds
        elif rating_diff > 10:  # Home stronger
            home_odds = round(random.uniform(1.50, 1.85), 2)
            draw_odds = round(random.uniform(3.80, 4.50), 2)
            away_odds = round(random.uniform(4.50, 7.00), 2)
        elif rating_diff > -10:  # Even match
            home_odds = round(random.uniform(2.20, 2.70), 2)
            draw_odds = round(random.uniform(3.00, 3.40), 2)
            away_odds = round(random.uniform(2.40, 2.90), 2)
        elif rating_diff > -20:  # Away stronger
            home_odds = round(random.uniform(4.00, 6.50), 2)
            draw_odds = round(random.uniform(3.80, 4.50), 2)
            away_odds = round(random.uniform(1.55, 1.90), 2)  # Away favorite
        else:  # Away much stronger
            home_odds = round(random.uniform(7.00, 14.00), 2)  # Home underdog
            draw_odds = round(random.uniform(5.00, 6.50), 2)
            away_odds = round(random.uniform(1.20, 1.50), 2)  # Away favorite
        
        # Calculate derived odds
        home_draw_odds = round(home_odds * draw_odds / (home_odds + draw_odds - 1), 2)
        home_away_odds = round(home_odds * away_odds / (home_odds + away_odds - 1), 2)
        draw_away_odds = round(draw_odds * away_odds / (draw_odds + away_odds - 1), 2)
        
        gg_odds = round(random.uniform(1.75, 2.10), 2)
        ng_odds = round(random.uniform(1.75, 2.10), 2)
        
        over15_odds = round(random.uniform(1.20, 1.40), 2)
        under15_odds = round(random.uniform(3.50, 5.00), 2)
        over25_odds = round(random.uniform(1.75, 2.10), 2)
        under25_odds = round(random.uniform(1.75, 2.10), 2)
        over35_odds = round(random.uniform(2.50, 3.20), 2)
        under35_odds = round(random.uniform(1.35, 1.60), 2)
        
        # Correct score odds (simplified)
        correct_scores = {
            "1-0": random.uniform(6.0, 8.0),
            "2-0": random.uniform(7.0, 9.0),
            "2-1": random.uniform(7.0, 9.0),
            "3-0": random.uniform(12.0, 16.0),
            "3-1": random.uniform(14.0, 18.0),
            "3-2": random.uniform(20.0, 28.0),
            "0-0": random.uniform(8.0, 11.0),
            "1-1": random.uniform(5.5, 7.0),
            "2-2": random.uniform(12.0, 16.0),
            "0-1": random.uniform(8.0, 11.0),
            "0-2": random.uniform(11.0, 15.0),
            "1-2": random.uniform(9.0, 12.0),
            "0-3": random.uniform(20.0, 28.0),
            "1-3": random.uniform(18.0, 24.0),
            "2-3": random.uniform(25.0, 35.0)
        }
        correct_score_odds = {k: round(v, 2) for k, v in correct_scores.items()}
        
        return {
            'home_odds': home_odds,
            'draw_odds': draw_odds,
            'away_odds': away_odds,
            'home_draw_odds': home_draw_odds,
            'home_away_odds': home_away_odds,
            'draw_away_odds': draw_away_odds,
            'gg_odds': gg_odds,
            'ng_odds': ng_odds,
            'over15_odds': over15_odds,
            'under15_odds': under15_odds,
            'over25_odds': over25_odds,
            'under25_odds': under25_odds,
            'over35_odds': over35_odds,
            'under35_odds': under35_odds,
            'correct_score_odds': json.dumps(correct_score_odds)
        }
    
    def create_game(self, league_id, home_team_id, away_team_id, scheduled_start, auto_play=True):
        """Create a new virtual game"""
        try:
            league = VirtualLeague.query.get(league_id)
            home_team = VirtualTeam.query.get(home_team_id)
            away_team = VirtualTeam.query.get(away_team_id)
            
            if not all([league, home_team, away_team]):
                raise ValueError("League or teams not found")
            
            # Generate odds based on team ratings
            odds = self.generate_odds(home_team.rating, away_team.rating)
            
            game = VirtualGame(
                league_id=league_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                scheduled_start=scheduled_start,
                game_duration=league.game_duration_seconds,
                is_auto_play=auto_play,
                **odds
            )
            
            db.session.add(game)
            db.session.commit()
            logger.info(f"[VirtualGame] Created game {game.id}")
            return game
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error creating game: {e}")
            raise
    
    def schedule_games_for_league(self, league_id, num_games=10, start_time=None):
        """Schedule multiple games for a league with unique team pairings - ALL START AT SAME TIME"""
        try:
            league = VirtualLeague.query.get(league_id)
            if not league:
                raise ValueError("League not found")
            
            teams = self.get_league_teams(league_id)
            if len(teams) < 2:
                raise ValueError("Need at least 2 teams to schedule games")
            
            # Ensure we have enough teams for requested matches
            if num_games * 2 > len(teams):
                raise ValueError(f"Cannot create {num_games} matches with only {len(teams)} teams. Need at least {num_games * 2} teams.")
            
            if not start_time:
                # Default: start 180 seconds (3 minutes) from now for countdown
                start_time = datetime.utcnow() + timedelta(seconds=180)
            
            games_created = []
            
            # Create a shuffled copy of teams to ensure each team plays once
            # Use timestamp and league ID to generate different matchups each time
            available_teams = teams.copy()
            
            # Seed shuffle with league ID and current timestamp for variety
            # This ensures different matchups for each race
            seed_value = f"{league_id}_{int(datetime.utcnow().timestamp() * 1000)}"
            random.seed(seed_value)
            random.shuffle(available_teams)
            random.seed()  # Reset seed to default random behavior
            
            # Pair teams sequentially: [0 vs 1, 2 vs 3, 4 vs 5, ...]
            # ALL GAMES START AT THE SAME TIME for synchronized racing
            for i in range(num_games):
                home_team = available_teams[i * 2]
                away_team = available_teams[i * 2 + 1]
                
                # ALL games use the SAME scheduled_time for synchronized start
                game = self.create_game(
                    league_id=league_id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    scheduled_start=start_time,  # ALL use same start time
                    auto_play=True
                )
                games_created.append(game)
            
            logger.info(f"[VirtualGame] Scheduled {len(games_created)} unique games for league {league_id} (each team plays once)")
            return games_created
        except Exception as e:
            logger.error(f"[VirtualGame] Error scheduling games: {e}")
            raise
    
    # ================== Game Management ==================
    
    def get_upcoming_games(self, league_id=None, limit=20):
        """Get upcoming scheduled games"""
        query = VirtualGame.query.filter_by(status=VirtualGameStatus.SCHEDULED.value)
        if league_id:
            query = query.filter_by(league_id=league_id)
        return query.order_by(VirtualGame.scheduled_start).limit(limit).all()
    
    def get_live_games(self, league_id=None):
        """Get currently live games"""
        query = VirtualGame.query.filter_by(status=VirtualGameStatus.LIVE.value)
        if league_id:
            query = query.filter_by(league_id=league_id)
        return query.all()
    
    def get_finished_games(self, league_id=None, limit=50):
        """Get finished games"""
        query = VirtualGame.query.filter_by(status=VirtualGameStatus.FINISHED.value)
        if league_id:
            query = query.filter_by(league_id=league_id)
        return query.order_by(VirtualGame.finished_at.desc()).limit(limit).all()
    
    def start_game(self, game_id):
        """Start a virtual game"""
        try:
            game = VirtualGame.query.get(game_id)
            if not game:
                raise ValueError("Game not found")
            
            if game.status != VirtualGameStatus.SCHEDULED.value:
                raise ValueError("Game is not in scheduled status")
            
            game.status = VirtualGameStatus.LIVE.value
            game.actual_start = datetime.utcnow()
            game.current_minute = 0
            
            db.session.commit()
            logger.info(f"[VirtualGame] Started game {game_id}")
            return game
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error starting game: {e}")
            raise
    
    def update_game_score(self, game_id, home_score, away_score, current_minute=None):
        """Update game score (admin control)"""
        try:
            game = VirtualGame.query.get(game_id)
            if not game:
                raise ValueError("Game not found")
            
            game.home_score = home_score
            game.away_score = away_score
            if current_minute is not None:
                game.current_minute = current_minute
            
            # Update half-time score if at half time
            if current_minute and current_minute >= 45 and game.ht_home_score is None:
                game.ht_home_score = home_score
                game.ht_away_score = away_score
            
            game.result_set_manually = True
            
            db.session.commit()
            logger.info(f"[VirtualGame] Updated game {game_id} score: {home_score}-{away_score}")
            return game
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error updating game score: {e}")
            raise
    
    def finish_game(self, game_id):
        """Finish a virtual game"""
        try:
            game = VirtualGame.query.get(game_id)
            if not game:
                raise ValueError("Game not found")
            
            game.status = VirtualGameStatus.FINISHED.value
            game.finished_at = datetime.utcnow()
            game.current_minute = 90
            
            db.session.commit()
            logger.info(f"[VirtualGame] Finished game {game_id}")
            
            # Settle bets for this game
            self._settle_game_bets(game)
            
            return game
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error finishing game: {e}")
            raise
    
    def simulate_game_auto(self, game_id):
        """Auto-simulate a game result based on team ratings"""
        try:
            game = VirtualGame.query.get(game_id)
            if not game:
                raise ValueError("Game not found")
            
            home_team = game.home_team
            away_team = game.away_team
            
            # Calculate goal probabilities based on ratings (more strict/realistic)
            rating_diff = home_team.rating - away_team.rating
            
            # Home goals (0-4) - reduced base probability for more realistic scores
            home_base_prob = 1.0 + (rating_diff / 40)  # Lower base and less rating impact
            home_goals = min(4, max(0, int(random.gauss(home_base_prob, 0.9))))  # Tighter distribution
            
            # Away goals (0-4) - reduced base probability
            away_base_prob = 1.0 - (rating_diff / 40)  # Lower base and less rating impact
            away_goals = min(4, max(0, int(random.gauss(away_base_prob, 0.9))))  # Tighter distribution
            
            # Extra strictness: reduce by 1 if both scores are high
            if home_goals + away_goals > 5:
                if random.random() < 0.6:  # 60% chance to reduce one score
                    if home_goals > away_goals:
                        home_goals = max(0, home_goals - 1)
                    else:
                        away_goals = max(0, away_goals - 1)
            
            # Half-time scores (roughly 35-45% of full-time)
            ht_home = int(home_goals * random.uniform(0.35, 0.45))
            ht_away = int(away_goals * random.uniform(0.35, 0.45))
            
            # Start the game
            self.start_game(game_id)
            
            # Update with final scores
            game.home_score = home_goals
            game.away_score = away_goals
            game.ht_home_score = ht_home
            game.ht_away_score = ht_away
            game.current_minute = 90
            
            db.session.commit()
            
            # Finish the game
            self.finish_game(game_id)
            
            logger.info(f"[VirtualGame] Auto-simulated game {game_id}: {home_goals}-{away_goals}")
            return game
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error auto-simulating game: {e}")
            raise
    
    def _settle_game_bets(self, game):
        """Settle all bets for a finished game"""
        from app.models import Bet, BetStatus
        
        try:
            # Find all pending/active bets for this virtual game
            bets = Bet.query.filter(
                Bet.match_id == game.id,
                Bet.status.in_([BetStatus.PENDING.value, BetStatus.ACTIVE.value]),
                Bet.bet_type == 'virtual'
            ).all()
            
            for bet in bets:
                is_win = self._check_bet_result(bet, game)
                
                if is_win:
                    bet.status = BetStatus.WON.value
                    bet.result = 'win'
                    bet.settled_payout = bet.potential_payout
                    # Credit user balance
                    bet.user.balance += bet.potential_payout
                else:
                    bet.status = BetStatus.LOST.value
                    bet.result = 'loss'
                    bet.settled_payout = 0
                
                bet.settled_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"[VirtualGame] Settled {len(bets)} bets for game {game.id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error settling bets: {e}")
    
    def _check_bet_result(self, bet, game):
        """Check if a bet won based on game result"""
        market = bet.market_type.lower() if bet.market_type else ''
        selection = bet.selection.lower() if bet.selection else ''
        
        home_score = game.home_score
        away_score = game.away_score
        total_goals = home_score + away_score
        
        # 1X2 (Match Result) - Handle '1', 'x', '2' and 'home', 'draw', 'away'
        if market == '1x2':
            if selection in ['1', 'home'] and home_score > away_score:
                return True
            if selection in ['x', 'draw'] and home_score == away_score:
                return True
            if selection in ['2', 'away'] and away_score > home_score:
                return True
        
        # Both Teams to Score (GG/NG)
        elif market == 'gg':
            if selection in ['gg', 'yes'] and home_score > 0 and away_score > 0:
                return True
            if selection in ['ng', 'no'] and (home_score == 0 or away_score == 0):
                return True
        
        # Over/Under (handle both 'ou15' and 'o/u' formats)
        elif market in ['ou15', 'o/u']:
            if selection == 'over' and total_goals > 2.5:  # Default to 2.5
                return True
            if selection == 'under' and total_goals < 2.5:
                return True
        elif market == 'ou25':
            if selection == 'over' and total_goals > 2.5:
                return True
            if selection == 'under' and total_goals < 2.5:
                return True
        elif market == 'ou35':
            if selection == 'over' and total_goals > 3.5:
                return True
            if selection == 'under' and total_goals < 3.5:
                return True
        
        # Correct Score
        elif market == 'cs':
            expected_score = selection  # e.g., "2-1"
            actual_score = f"{home_score}-{away_score}"
            if expected_score == actual_score:
                return True
        
        return False
    
    def delete_game(self, game_id):
        """Delete a game"""
        try:
            game = VirtualGame.query.get(game_id)
            if not game:
                raise ValueError("Game not found")
            
            db.session.delete(game)
            db.session.commit()
            logger.info(f"[VirtualGame] Deleted game {game_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error deleting game: {e}")
            raise
    
    def clear_all_games(self, league_id=None):
        """Clear all games for a league or all leagues"""
        try:
            if league_id:
                games = VirtualGame.query.filter_by(league_id=league_id).all()
                logger.info(f"[VirtualGame] Clearing {len(games)} games for league {league_id}")
            else:
                games = VirtualGame.query.all()
                logger.info(f"[VirtualGame] Clearing all {len(games)} games")
            
            for game in games:
                db.session.delete(game)
            
            db.session.commit()
            return len(games)
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualGame] Error clearing games: {e}")
            raise
    
    def reset_league(self, league_id):
        """Reset a league - clear all games and start fresh"""
        try:
            games_deleted = self.clear_all_games(league_id)
            logger.info(f"[VirtualGame] Reset league {league_id}: deleted {games_deleted} games")
            return {
                'games_deleted': games_deleted,
                'teams_count': len(self.get_league_teams(league_id))
            }
        except Exception as e:
            logger.error(f"[VirtualGame] Error resetting league: {e}")
            raise
    
    def settle_all_virtual_bets(self):
        """Auto-settle all pending virtual bets where all games are finished"""
        from app.models import Bet, BetStatus, User
        
        try:
            # Get all pending virtual bets
            pending_bets = Bet.query.filter_by(
                bet_type='virtual',
                status='pending'
            ).all()
            
            settled_count = 0
            
            for bet in pending_bets:
                try:
                    # Parse the selections JSON
                    selections = json.loads(bet.selection)
                    
                    # Check if ALL games in this bet are finished
                    all_finished = True
                    all_won = True
                    
                    for sel in selections:
                        game = VirtualGame.query.get(sel['game_id'])
                        if not game or game.status != VirtualGameStatus.FINISHED.value:
                            all_finished = False
                            break
                        
                        # Check if this selection won
                        market = sel.get('market', '1X2').lower()
                        selection = sel.get('selection', '').lower()
                        
                        won = self._check_virtual_selection(game, market, selection)
                        if not won:
                            all_won = False
                    
                    # Only settle if all games are finished
                    if all_finished:
                        if all_won:
                            # All selections won - pay out
                            bet.status = BetStatus.WON.value
                            bet.result = 'win'
                            bet.settled_payout = bet.potential_payout
                            # Credit user balance
                            bet.user.balance += bet.potential_payout
                            logger.info(f"[VirtualBet] Bet {bet.id} WON - paid ${bet.potential_payout:.2f}")
                        else:
                            # At least one selection lost
                            bet.status = BetStatus.LOST.value
                            bet.result = 'loss'
                            bet.settled_payout = 0
                            logger.info(f"[VirtualBet] Bet {bet.id} LOST")
                        
                        bet.settled_at = datetime.utcnow()
                        settled_count += 1
                
                except Exception as e:
                    logger.error(f"[VirtualBet] Error settling bet {bet.id}: {e}")
                    continue
            
            db.session.commit()
            logger.info(f"[VirtualBet] Auto-settled {settled_count} virtual bets")
            return settled_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"[VirtualBet] Error in auto-settlement: {e}")
            return 0
    
    def _check_virtual_selection(self, game, market, selection):
        """Check if a single virtual bet selection won"""
        home_score = game.home_score
        away_score = game.away_score
        total_goals = home_score + away_score
        
        # 1X2 (Match Result)
        if market == '1x2':
            if selection in ['1', 'home'] and home_score > away_score:
                return True
            if selection in ['x', 'draw'] and home_score == away_score:
                return True
            if selection in ['2', 'away'] and away_score > home_score:
                return True
        
        # Double Chance
        elif market == 'dc':
            if selection == '1x' and home_score >= away_score:
                return True
            if selection == '12' and home_score != away_score:
                return True
            if selection == 'x2' and away_score >= home_score:
                return True
        
        # Both Teams to Score
        elif market == 'gg':
            if selection in ['gg', 'yes'] and home_score > 0 and away_score > 0:
                return True
            if selection in ['ng', 'no'] and (home_score == 0 or away_score == 0):
                return True
        
        # Over/Under 2.5
        elif market == 'o/u':
            if selection == 'over' and total_goals > 2.5:
                return True
            if selection == 'under' and total_goals < 2.5:
                return True
        
        return False
