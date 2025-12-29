from app.models import db, Bet, BetStatus, User
from datetime import datetime, timedelta
import logging
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from types import SimpleNamespace

logger = logging.getLogger(__name__)

class BettingService:
    """Service for betting operations"""
    
    def create_bet(self, user: User, amount: float, odds: float, 
                   bet_type: str, event_description: str,
                   market_type: str = None, selection: str = None, 
                   booking_code: str = None, match_id: int = None) -> Bet:
        """Create a new bet"""
        try:
            if user.balance < amount:
                raise ValueError("Insufficient balance")
            
            potential_payout = amount * odds
            
            bet = Bet(
                user_id=user.id,
                match_id=match_id,
                amount=amount,
                odds=odds,
                potential_payout=potential_payout,
                market_type=market_type,
                selection=selection,
                bet_type=bet_type,
                event_description=event_description,
                booking_code=booking_code,
                status=BetStatus.ACTIVE.value,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            
            # Deduct from balance
            user.balance -= amount
            
            db.session.add(bet)
            db.session.commit()
            logger.info(f"Bet created for user {user.username}: {amount} BTC at {odds} odds")
            return bet
        except Exception as e:
            logger.error(f"Error creating bet: {e}")
            db.session.rollback()
            raise
    
    def settle_bet(self, bet: Bet, result: str, actual_payout: float = None) -> bool:
        """Settle a bet"""
        try:
            if result not in ['win', 'loss']:
                raise ValueError("Result must be 'win' or 'loss'")
            
            bet.result = result
            bet.settled_at = datetime.utcnow()
            
            if result == 'win':
                payout = actual_payout or bet.potential_payout
                bet.settled_payout = payout
                bet.user.balance += payout
                bet.status = BetStatus.WON.value
                logger.info(f"Bet won: {bet.id} - Payout: {payout} BTC")
            else:
                bet.settled_payout = 0
                bet.status = BetStatus.LOST.value
                logger.info(f"Bet lost: {bet.id}")
            
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error settling bet: {e}")
            db.session.rollback()
            return False
    
    def cancel_bet(self, bet: Bet, refund: bool = True) -> bool:
        """Cancel a bet"""
        try:
            if bet.status != BetStatus.ACTIVE.value:
                raise ValueError("Can only cancel active bets")
            
            if refund:
                bet.user.balance += bet.amount
                logger.info(f"Bet cancelled and refunded: {bet.id}")
            
            bet.status = BetStatus.CANCELLED.value
            bet.settled_at = datetime.utcnow()
            
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error cancelling bet: {e}")
            db.session.rollback()
            return False
    
    def get_user_bets(self, user: User, status: str = None) -> list:
        """Get user's bets"""
        # Try the normal ORM query first; if the database schema is missing
        # recently added columns (causing OperationalError), fall back to a
        # raw SQL projection that only selects stable columns.
        try:
            query = Bet.query.filter_by(user_id=user.id)
            if status:
                query = query.filter_by(status=status)
            return query.order_by(Bet.created_at.desc()).all()
        except OperationalError:
            logger.warning("DB schema missing newer columns; using raw-SQL fallback for user bets")
            # Safe column list that existed in older schema
            cols = [
                'id', 'user_id', 'amount', 'odds', 'potential_payout',
                'bet_type', 'event_description', 'status', 'result',
                'settled_payout', 'created_at', 'settled_at', 'expires_at',
                'market_type', 'selection'
            ]
            # Try with all columns first; if any are missing, catch and remove
            sql = f"SELECT {', '.join(cols)} FROM bets WHERE user_id = :uid"
            params = {'uid': user.id}
            if status:
                sql += " AND status = :status"
                params['status'] = status
            sql += " ORDER BY created_at DESC"
            try:
                res = db.session.execute(text(sql), params)
                rows = res.fetchall()
            except Exception:
                # If columns don't exist, try without market_type/selection
                logger.warning("Fallback projection failed including market columns; retrying without them")
                cols_safe = [
                    'id', 'user_id', 'amount', 'odds', 'potential_payout',
                    'bet_type', 'event_description', 'status', 'result',
                    'settled_payout', 'created_at', 'settled_at', 'expires_at'
                ]
                sql = f"SELECT {', '.join(cols_safe)} FROM bets WHERE user_id = :uid"
                if status:
                    sql += " AND status = :status"
                sql += " ORDER BY created_at DESC"
                try:
                    res = db.session.execute(text(sql), params)
                    rows = res.fetchall()
                    cols = cols_safe
                except Exception:
                    # If the table truly doesn't exist, return an empty list
                    logger.error("Bets table missing or inaccessible during fallback projection")
                    return []
            # Map rows to lightweight objects (SimpleNamespace) to preserve attribute access
            bets = []
            for r in rows:
                row_dict = dict(zip(cols, r))
                # Normalize date/time fields so callers can safely call .isoformat()
                for dt_field in ('created_at', 'settled_at', 'expires_at'):
                    v = row_dict.get(dt_field)
                    if isinstance(v, str):
                        try:
                            row_dict[dt_field] = datetime.fromisoformat(v)
                        except Exception:
                            # leave as-is if parsing fails
                            pass

                obj = SimpleNamespace(**row_dict)
                bets.append(obj)
            return bets
    
    def get_active_bets(self, user: User) -> list:
        """Get active bets for a user (excluding cashed out bets)"""
        try:
            # Get only active bets that haven't been cashed out
            active_bets = Bet.query.filter_by(
                user_id=user.id, 
                status=BetStatus.ACTIVE.value,
                is_cashed_out=False
            ).all()
            return active_bets
        except OperationalError:
            # Fallback if is_cashed_out column doesn't exist
            logger.warning("is_cashed_out column not found, falling back to active bets only")
            return self.get_user_bets(user, status=BetStatus.ACTIVE.value)
    
    def get_user_statistics(self, user: User) -> dict:
        """Get user betting statistics"""
        try:
            bets = Bet.query.filter_by(user_id=user.id).all()
        except OperationalError:
            logger.warning("DB schema missing newer columns; using raw-SQL fallback for statistics")
            # Fallback to raw SQL projection if schema is missing newer cols
            cols = [
                'id', 'user_id', 'amount', 'odds', 'potential_payout',
                'bet_type', 'event_description', 'status', 'result',
                'settled_payout', 'created_at', 'settled_at', 'expires_at',
                'market_type', 'selection'
            ]
            sql = f"SELECT {', '.join(cols)} FROM bets WHERE user_id = :uid"
            try:
                res = db.session.execute(text(sql), {'uid': user.id})
                rows = res.fetchall()
                # Convert rows to SimpleNamespace objects and normalize datetimes
                bets = []
                for r in rows:
                    row = dict(zip(cols, r))
                    for dt_field in ('created_at', 'settled_at', 'expires_at'):
                        v = row.get(dt_field)
                        if isinstance(v, str):
                            try:
                                row[dt_field] = datetime.fromisoformat(v)
                            except Exception:
                                pass
                    bets.append(SimpleNamespace(**row))
            except Exception:
                logger.warning("Fallback projection for statistics failed including market columns; retrying without them")
                # If columns don't exist, try without market_type/selection
                cols_safe = [
                    'id', 'user_id', 'amount', 'odds', 'potential_payout',
                    'bet_type', 'event_description', 'status', 'result',
                    'settled_payout', 'created_at', 'settled_at', 'expires_at'
                ]
                try:
                    res = db.session.execute(text(f"SELECT {', '.join(cols_safe)} FROM bets WHERE user_id = :uid"), {'uid': user.id})
                    rows = res.fetchall()
                    bets = [SimpleNamespace(**dict(zip(cols_safe, r))) for r in rows]
                except Exception:
                    bets = []

        # Compute statistics defensively so bets may be ORM objects or dicts
        def get_attr(b, key):
            if isinstance(b, dict):
                return b.get(key)
            return getattr(b, key, None)

        total_bets = len(bets)
        won_bets = len([b for b in bets if get_attr(b, 'result') == 'win'])
        lost_bets = len([b for b in bets if get_attr(b, 'result') == 'loss'])
        active_bets = len([b for b in bets if get_attr(b, 'status') == BetStatus.ACTIVE.value])

        total_wagered = sum(get_attr(b, 'amount') or 0 for b in bets)
        total_payout = sum((get_attr(b, 'settled_payout') or 0) for b in bets)

        win_rate = (won_bets / total_bets * 100) if total_bets > 0 else 0
        roi = ((total_payout - total_wagered) / total_wagered * 100) if total_wagered > 0 else 0

        return {
            'total_bets': total_bets,
            'won_bets': won_bets,
            'lost_bets': lost_bets,
            'active_bets': active_bets,
            'total_wagered': total_wagered,
            'total_payout': total_payout,
            'win_rate': round(win_rate, 2),
            'roi': round(roi, 2)
        }

    def get_bet_match_scores(self, bet: Bet):
        """Extract match scores for a bet (handles multi-bets)"""
        from app.models import Match
        import re
        
        # If bet has a direct match reference, return single match score
        if bet.match:
            return {
                'home_team': bet.match.home_team,
                'away_team': bet.match.away_team,
                'home_score': bet.match.home_score,
                'away_score': bet.match.away_score,
                'status': bet.match.status
            }
        
        # For multi-bets, extract match names and find scores
        if 'MULTI:' in bet.event_description:
            match_scores = []
            picks = bet.event_description.replace('MULTI: ', '').split(' | ')
            
            for pick in picks:
                # Extract match name (e.g., "Arsenal vs Chelsea")
                match_pattern = r'^(.+?)\s+\['
                match_result = re.match(match_pattern, pick)
                if match_result:
                    match_name = match_result.group(1).strip()
                    
                    # Try to find the match in database
                    # Match format is usually "Home Team vs Away Team"
                    if ' vs ' in match_name:
                        teams = match_name.split(' vs ')
                        if len(teams) == 2:
                            home_team, away_team = teams[0].strip(), teams[1].strip()
                            match = Match.query.filter(
                                Match.home_team.like(f'%{home_team}%'),
                                Match.away_team.like(f'%{away_team}%')
                            ).first()
                            
                            if match:
                                match_scores.append({
                                    'home_team': match.home_team,
                                    'away_team': match.away_team,
                                    'home_score': match.home_score,
                                    'away_score': match.away_score,
                                    'status': match.status
                                })
                            else:
                                match_scores.append(None)
                        else:
                            match_scores.append(None)
                    else:
                        match_scores.append(None)
                else:
                    match_scores.append(None)
            
            return match_scores if match_scores else None
        
        return None
