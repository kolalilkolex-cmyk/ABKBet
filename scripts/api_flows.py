import sys, os, requests, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

BASE = 'http://127.0.0.1:5000'

# Use sample user 'alice' created earlier
USERNAME = 'alice'
PASSWORD = 'AlicePass123!'


def login():
    r = requests.post(f'{BASE}/api/auth/login', json={'username': USERNAME, 'password': PASSWORD})
    print('LOGIN', r.status_code, r.text)
    if r.status_code == 200:
        return r.json().get('access_token')
    return None


def place_bet(token):
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        'amount': 0.0002,
        'odds': 2.0,
        'bet_type': 'sports',
        'event_description': 'Team A vs Team B - friendly'
    }
    r = requests.post(f'{BASE}/api/bets', json=payload, headers=headers)
    print('PLACE BET', r.status_code, r.text)
    if r.status_code == 201:
        return r.json()['bet']['id']
    return None


def cancel_bet(token, bet_id):
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.post(f'{BASE}/api/bets/{bet_id}/cancel', headers=headers)
    print('CANCEL BET', r.status_code, r.text)


def simulate_deposit(token, amount=0.0005):
    # Create a transaction record directly via API isn't provided; we'll create one using admin endpoint if available,
    # otherwise create via a helper endpoint — fallback: use webhook to update a nonexistent tx -> create tx manually via DB
    # Simpler: use /api/payment/wallet to get address, then create a Transaction via an admin route if present. Let's try admin route.
    headers = {'Authorization': f'Bearer {token}'}
    # Try admin create transaction endpoint
    admin_url = f'{BASE}/api/admin/create-transaction'
    payload = {
        'user_id': None,
        'tx_hash': f'simulated_tx_{int(time.time())}',
        'amount': amount,
        'transaction_type': 'deposit',
        'to_address': None
    }
    # Need user id and wallet address
    # get profile first
    r = requests.get(f'{BASE}/api/auth/profile', headers=headers)
    if r.status_code != 200:
        print('Profile fetch failed; cannot simulate deposit')
        return
    user = r.json()['user']
    payload['user_id'] = user['id']

    # get wallet address
    r2 = requests.get(f'{BASE}/api/payment/wallet', headers=headers)
    if r2.status_code != 200:
        print('Wallet fetch failed; cannot simulate deposit')
        return
    wallet = r2.json()['wallet']
    payload['to_address'] = wallet['bitcoin_address']

    # Try admin endpoint
    r3 = requests.post(admin_url, json=payload, headers=headers)
    if r3.status_code == 404:
        print('Admin create-transaction endpoint not available. Creating transaction via webhook simulation...')
        # Create Transaction by calling webhook but first create a Transaction in DB via admin is missing.
        # As fallback, call webhook with tx_hash that doesn't exist -> will return 404. So we'll create transaction via a helper script in-process.
        print('Running in-process DB insert (via local script).')
        create_tx_in_db(payload)
        # Now call webhook to confirm it
        import json
        webhook_body = {'tx_hash': payload['tx_hash'], 'confirmations': 1}
        # Build the exact payload string we'll send (requests.json would encode similarly)
        payload_json = json.dumps(webhook_body)
        webhook_sig = generate_sig(payload_json)
        headers = {'X-Signature': webhook_sig, 'Content-Type': 'application/json'}
        r4 = requests.post(f'{BASE}/api/webhook/transaction-confirmation', data=payload_json, headers=headers)
        print('WEBHOOK CONFIRM', r4.status_code, r4.text)
    else:
        print('ADMIN CREATE TX', r3.status_code, r3.text)


def create_tx_in_db(payload):
    # Create a transaction in-process using app context (no external process)
    try:
        from run import create_app
        from app.models import db, Transaction
        from datetime import datetime

        app = create_app()
        with app.app_context():
            tx = Transaction(
                user_id=payload['user_id'],
                tx_hash=payload['tx_hash'],
                amount=payload['amount'],
                transaction_type=payload['transaction_type'],
                status='pending',
                to_address=payload['to_address'],
                created_at=datetime.utcnow()
            )
            db.session.add(tx)
            db.session.commit()
            print('Inserted tx in DB:', tx.tx_hash)
    except Exception as e:
        print('Error inserting tx in DB:', e)


def generate_sig(payload_str):
    # For webhook signature we use default secret 'webhook-secret' and HMAC-SHA256 over raw payload string
    import hmac, hashlib
    secret = os.getenv('WEBHOOK_SECRET', 'webhook-secret')
    if isinstance(payload_str, dict):
        import json
        payload_str = json.dumps(payload_str, separators=(',', ':'), sort_keys=True)
    return hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()


if __name__=='__main__':
    token = login()
    if not token:
        print('Login failed; aborting flows')
        sys.exit(1)
    bet_id = place_bet(token)
    if bet_id:
        time.sleep(1)
        cancel_bet(token, bet_id)
    simulate_deposit(token, amount=0.0005)
