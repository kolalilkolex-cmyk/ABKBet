#!/usr/bin/env python3
"""Simple smoke test for the ABKBet API.

Workflow:
- Register a new user
- Login (obtain access token)
- Fund the user via admin `/api/admin/fund-user` (uses X-Admin-Token header)
- Create a bet (include `market_type` and `selection`)
- GET `/api/bets/active` and `/api/bets/statistics` and assert expected fields

Usage: run in the project venv: `python smoke_test.py`
"""
import os
import time
import uuid
import requests

BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-secret')


def now_tag():
    return uuid.uuid4().hex[:8]


def register(username, email, password='Test1234!'):
    url = f"{BASE_URL}/api/auth/register"
    r = requests.post(url, json={'username': username, 'email': email, 'password': password})
    return r


def login(username, password='Test1234!'):
    url = f"{BASE_URL}/api/auth/login"
    r = requests.post(url, json={'username': username, 'password': password})
    return r


def skrill_deposit(token, reference, amount):
    url = f"{BASE_URL}/api/payment/deposit/skrill"
    headers = {'Authorization': f"Bearer {token}"}
    payload = {'reference_id': reference, 'amount': amount}
    r = requests.post(url, json=payload, headers=headers)
    return r


def create_bet(token, payload):
    url = f"{BASE_URL}/api/bets"
    headers = {'Authorization': f"Bearer {token}"}
    r = requests.post(url, json=payload, headers=headers)
    return r


def get_wallet(token):
    url = f"{BASE_URL}/api/payment/wallet"
    headers = {'Authorization': f"Bearer {token}"}
    return requests.get(url, headers=headers)


def get_active(token):
    url = f"{BASE_URL}/api/bets/active"
    headers = {'Authorization': f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    return r


def get_statistics(token):
    url = f"{BASE_URL}/api/bets/statistics"
    headers = {'Authorization': f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    return r


def main():
    tag = now_tag()
    username = f"smoketest_{tag}"
    email = f"{username}@example.local"
    password = 'Test1234!'

    print('1) Registering user...')
    r = register(username, email, password)
    print(r.status_code, r.text)
    if r.status_code not in (200, 201):
        print('Register failed, aborting')
        return 1

    data = r.json()
    user_id = data.get('user', {}).get('id')
    if not user_id:
        print('No user id returned, aborting')
        return 1

    print('2) Logging in...')
    r = login(username, password)
    print(r.status_code, r.text)
    if r.status_code != 200:
        print('Login failed, aborting')
        return 1
    token = r.json().get('access_token')
    if not token:
        print('No token returned, aborting')
        return 1

    print('3) Ensure user wallet exists (GET /api/payment/wallet)')
    r = get_wallet(token)
    print(r.status_code, r.text)
    if r.status_code != 200:
        print('Failed to create/get wallet, aborting')
        return 1

    print('4) Funding user via Skrill-like deposit endpoint...')
    ref = f"smoke-skrill-{tag}"
    r = skrill_deposit(token, ref, 10.0)
    print(r.status_code, r.text)
    if r.status_code != 200:
        print('Funding failed, aborting')
        return 1
    time.sleep(0.5)

    print('5) Creating a bet...')
    payload = {
        'amount': 5.0,
        'odds': 1.8,
        'bet_type': 'single',
        'event_description': 'Test Match - smoketest',
        'market_type': '1X2',
        'selection': 'home'
    }
    r = create_bet(token, payload)
    print(r.status_code, r.text)
    if r.status_code not in (200, 201):
        print('Create bet failed, aborting')
        return 1

    print('5) Fetching active bets...')
    r = get_active(token)
    print(r.status_code, r.text)
    if r.status_code != 200:
        print('Get active bets failed')
        return 1
    active = r.json()
    # simple check for market_type and selection present
    bets = active.get('active_bets', [])
    if not bets:
        print('No active bets returned')
        return 1
    b = bets[0]
    print('Active bet sample:', b)
    if 'market_type' not in b or 'selection' not in b:
        print('market_type or selection missing in active bet')
        return 1

    print('6) Fetching statistics...')
    r = get_statistics(token)
    print(r.status_code, r.text)
    if r.status_code != 200:
        print('Get statistics failed')
        return 1

    print('\nSMOKE TEST PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
