print("✅ payment_core.py loaded from:", __file__)
from app.models import db, User, Transaction, TransactionStatus, Wallet
from app.services.bitcoin_service import BitcoinService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PaymentCore:
    def __init__(self, bitcoin_network: str = 'testnet'):
        print("✅ PaymentCore initialized with:", bitcoin_network)
        self.bitcoin_service = BitcoinService(network=bitcoin_network)

    def get_or_create_wallet(self, user):
        try:
            if getattr(user, 'wallet', None):
                return user.wallet
            # Generate a new address and create a Wallet record
            address = self.bitcoin_service.generate_address()
            wallet = Wallet(
                user_id=user.id,
                bitcoin_address=address,
                total_received=0.0,
                total_sent=0.0
            )
            db.session.add(wallet)
            db.session.commit()
            logger.info(f"Created wallet for user {user.username}: {address}")
            return wallet
        except Exception as e:
            logger.error(f"Error creating/getting wallet: {e}")
            db.session.rollback()
            raise

    def get_user_balance(self, user):
        try:
            return getattr(user, 'balance', 0.0) or 0.0
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return 0.0

    def get_transaction_history(self, user, limit: int = 50):
        try:
            return Transaction.query.filter_by(user_id=user.id).order_by(Transaction.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching transaction history: {e}")
            return []

    def process_skrill_deposit(self, user, reference_id, amount):
        try:
            # Re-fetch the user within the current DB session to avoid detached-instance issues
            db_user = User.query.get(user.id)

            logger.info(f"Processing Skrill deposit: user_id={user.id}, ref={reference_id}, amount={amount}")
            logger.debug(f"User before deposit: id={getattr(db_user,'id',None)}, balance={getattr(db_user,'balance',None)}")

            to_address = None
            if getattr(db_user, 'wallet', None):
                to_address = db_user.wallet.bitcoin_address
            else:
                logger.info(f"No wallet found for user {user.id} when processing Skrill deposit; creating one")
                try:
                    wallet = self.get_or_create_wallet(db_user)
                    to_address = wallet.bitcoin_address
                except Exception as w_err:
                    logger.exception(f"Failed creating wallet during Skrill deposit: {w_err}")
                    # proceed with None to_address, transaction may still record

            tx = Transaction(
                user_id=db_user.id,
                tx_hash=reference_id,
                amount=amount,
                transaction_type='deposit',
                status='pending',  # Changed to pending for admin approval
                payment_method='skrill',
                to_address=to_address
            )

            # Do NOT update balance yet - wait for admin approval
            # db_user.balance = (db_user.balance or 0.0) + amount

            db.session.add(tx)
            db.session.commit()
            logger.info(f"Skrill deposit submitted for approval: user {db_user.username} (ref={reference_id})")
            return True
        except Exception as e:
            # Ensure the full traceback is printed to stdout so it appears in the dev server log
            import traceback
            print("[payment_core] Skrill deposit exception:", type(e), repr(e))
            traceback.print_exc()
            logger.exception("Skrill deposit error")
            try:
                db.session.rollback()
            except Exception:
                logger.exception("Failed rolling back DB session after Skrill deposit error")
            # Re-raise the exception so route-level handlers can log full traceback to the configured app logger
            raise

    def process_eversend_deposit(self, user, reference_id, amount):
        try:
            # TODO: Add actual Eversend API verification here
            tx = Transaction(
                user_id=user.id,
                tx_hash=reference_id,
                amount=amount,
                transaction_type='deposit',
                status='pending',
                payment_method='eversend',
                to_address=user.wallet.bitcoin_address if user.wallet else None
            )
            # user.balance = (user.balance or 0.0) + amount  # Wait for admin approval
            db.session.add(tx)
            db.session.commit()
            logger.info(f"Eversend deposit submitted for approval: user {user.username}")
            return True
        except Exception as e:
            logger.exception(f"Revolut deposit error: {e}")
            db.session.rollback()
            return False

    def process_eversend_deposit(self, user, reference_id, amount):
        try:
            # TODO: Add actual Eversend API verification here
            tx = Transaction(
                user_id=user.id,
                tx_hash=reference_id,
                amount=amount,
                transaction_type='deposit',
                status='pending',  # Changed to pending for admin approval
                payment_method='eversend',
                to_address=user.wallet.bitcoin_address if user.wallet else None
            )
            # Do NOT update balance yet - wait for admin approval
            # user.balance = (user.balance or 0.0) + amount
            db.session.add(tx)
            db.session.commit()
            logger.info(f"Eversend deposit submitted for approval: user {user.username}")
            return True
        except Exception as e:
            logger.exception(f"Eversend deposit error: {e}")
            db.session.rollback()
            return False