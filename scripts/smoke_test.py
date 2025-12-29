import sys
import os
import json

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from run import create_app

app = create_app()

import time

with app.test_client() as c:
    print('-> GET /api/health')
    r = c.get('/api/health')
    print(r.status_code, r.get_data(as_text=True))

    # Use a unique username each run to avoid conflicts
    uname = f"smoketest_{int(time.time())}"
    email = f"{uname}@example.com"
    password = 'TestPass123!'

    # Try register
    print('\n-> POST /api/auth/register')
    payload = {'username': uname, 'password': password, 'email': email}
    r = c.post('/api/auth/register', json=payload)
    print(r.status_code, r.get_data(as_text=True))

    # Try login
    print('\n-> POST /api/auth/login')
    login_payload = {'username': uname, 'password': password}
    r = c.post('/api/auth/login', json=login_payload)
    print(r.status_code, r.get_data(as_text=True))
    token = None
    try:
        data = r.get_json()
        token = data.get('access_token') or data.get('token') or data.get('access')
    except Exception:
        token = None

    # If token present, test wallet endpoint
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        print('\n-> GET /api/payment/wallet (with auth)')
        r = c.get('/api/payment/wallet', headers=headers)
        print(r.status_code, r.get_data(as_text=True))
    else:
        print('\nNo token received from login; skipping wallet test')
