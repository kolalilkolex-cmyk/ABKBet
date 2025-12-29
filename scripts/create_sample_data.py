import sys
import os
import random
from datetime import datetime, timedelta

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from run import create_app
from app.models import db, User, Bet
from app.utils.auth import hash_password
from app.services.payment_core import PaymentCore
app = create_app()

SAMPLE_USERS = [
    {'username': 'alice', 'email': 'alice@example.com', 'password': 'AlicePass123!'},
    {'username': 'bob', 'email': 'bob@example.com', 'password': 'BobPass123!'},
    {'username': 'carol', 'email': 'carol@example.com', 'password': 'CarolPass123!'},
]

SAMPLE_BETS = [
    {'bet_type': 'sports', 'event': 'Team A vs Team B', 'odds': 1.8},
    {'bet_type': 'esports', 'event': 'Squad X vs Squad Y', 'odds': 2.5},
    {'bet_type': 'crypto', 'event': 'BTC price over $60k', 'odds': 3.0},
]


def seed():
    with app.app_context():
        payment_service = PaymentCore(bitcoin_network='testnet')

        created_users = []
        for u in SAMPLE_USERS:
            # skip if username/email exists
            existing = User.query.filter((User.username == u['username']) | (User.email == u['email'])).first()
            if existing:
                print(f"Skipping existing user: {existing.username} ({existing.email})")
                created_users.append(existing)
                continue

            user = User(
                username=u['username'],
                email=u['email'],
                password_hash=hash_password(u['password']),
                balance=0.0,
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            print(f"Created user: {user.username} (id={user.id})")

            # create wallet
            wallet = payment_service.get_or_create_wallet(user)
            print(f"  Wallet: {wallet.bitcoin_address}")

            created_users.append(user)

        # Create sample bets for each user
        for user in created_users:
            for i in range(2):
                b = random.choice(SAMPLE_BETS)
                amount = round(random.uniform(0.0001, 0.001), 8)
                odds = b['odds']
                payout = round(amount * odds, 8)
                bet = Bet(
                    user_id=user.id,
                    amount=amount,
                    odds=odds,
                    potential_payout=payout,
                    bet_type=b['bet_type'],
                    event_description=b['event'],
                    status='pending',
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=1)
                )
                db.session.add(bet)
                print(f"Added bet for {user.username}: {bet.bet_type} {bet.event_description} amount={amount} odds={odds}")
        db.session.commit()
        print("Sample data creation complete.")


if __name__ == '__main__':
    seed()
