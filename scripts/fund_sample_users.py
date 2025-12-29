import os, requests, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

BASE = 'http://127.0.0.1:5000'
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-secret')
HEADERS = {'X-Admin-Token': ADMIN_TOKEN, 'Content-Type': 'application/json'}

SAMPLES = [
    {'username': 'alice', 'amount': 0.001},
    {'username': 'bob', 'amount': 0.0015},
    {'username': 'carol', 'amount': 0.002}
]

# Helper to find user id
def get_users():
    # This endpoint requires a JWT; list_users in admin requires token. We'll query auth/profile by logging in.
    pass

if __name__ == '__main__':
    # Query the DB in-process to find user ids, then call the admin endpoint over HTTP
    try:
        from run import create_app
        from app.models import User
        app = create_app()
        with app.app_context():
            users = {u.username: u.id for u in User.query.all()}
    except Exception as e:
        print('Failed to fetch users from DB:', e)
        sys.exit(1)

    for s in SAMPLES:
        uname = s['username']
        uid = users.get(uname)
        if not uid:
            print(f'User not found: {uname}')
            continue
        payload = {'user_id': uid, 'amount': s['amount']}
        r = requests.post(f'{BASE}/api/admin/fund-user', json=payload, headers=HEADERS)
        print(uname, r.status_code, r.text)
