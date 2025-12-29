import sys, os, requests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

BASE = 'http://127.0.0.1:5000'

def login(username, password):
    r = requests.post(f'{BASE}/api/auth/login', json={'username': username, 'password': password})
    print('LOGIN', r.status_code, r.text)
    if r.status_code==200:
        return r.json().get('access_token')
    return None

def profile(token):
    headers={'Authorization': f'Bearer {token}'}
    r = requests.get(f'{BASE}/api/auth/profile', headers=headers)
    print('PROFILE', r.status_code, r.text)

def wallet(token):
    headers={'Authorization': f'Bearer {token}'}
    r = requests.get(f'{BASE}/api/payment/wallet', headers=headers)
    print('WALLET', r.status_code, r.text)

def bets_list(token):
    headers={'Authorization': f'Bearer {token}'}
    r = requests.get(f'{BASE}/api/bets/user/all', headers=headers)
    print('BETS', r.status_code, r.text)

if __name__=='__main__':
    # Use sample user alice
    token = login('alice', 'AlicePass123!')
    if not token:
        print('Login failed')
        sys.exit(1)
    profile(token)
    wallet(token)
    bets_list(token)
