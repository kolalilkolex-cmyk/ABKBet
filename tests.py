"""
Unit tests for ABKBet application
"""

import unittest
import json
from datetime import datetime
from run import create_app
from app.models import db, User, Bet, Wallet, Transaction
from config import config

class APITestCase(unittest.TestCase):
    """Base test case for API endpoints"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def register(self, username, email, password):
        """Helper method to register a user"""
        return self.client.post('/api/auth/register', data=json.dumps({
            'username': username,
            'email': email,
            'password': password
        }), content_type='application/json')
    
    def login(self, username, password):
        """Helper method to login a user"""
        return self.client.post('/api/auth/login', data=json.dumps({
            'username': username,
            'password': password
        }), content_type='application/json')

class AuthTestCase(APITestCase):
    """Test authentication endpoints"""
    
    def test_register_user(self):
        """Test user registration"""
        response = self.register('testuser', 'test@example.com', 'password123')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['username'], 'testuser')
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        self.register('testuser', 'test1@example.com', 'password123')
        response = self.register('testuser', 'test2@example.com', 'password123')
        self.assertEqual(response.status_code, 409)
    
    def test_login(self):
        """Test user login"""
        self.register('testuser', 'test@example.com', 'password123')
        response = self.login('testuser', 'password123')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
    
    def test_login_invalid_password(self):
        """Test login with invalid password"""
        self.register('testuser', 'test@example.com', 'password123')
        response = self.login('testuser', 'wrongpassword')
        self.assertEqual(response.status_code, 401)

class BettingTestCase(APITestCase):
    """Test betting endpoints"""
    
    def setUp(self):
        """Set up test case with registered user"""
        super().setUp()
        response = self.register('testuser', 'test@example.com', 'password123')
        data = json.loads(response.data)
        self.token = data['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    def test_create_bet(self):
        """Test creating a bet"""
        # First fund the user account
        user = User.query.filter_by(username='testuser').first()
        user.balance = 1.0  # 1 BTC
        db.session.commit()
        
        response = self.client.post('/api/bets', data=json.dumps({
            'amount': 0.1,
            'odds': 2.5,
            'bet_type': 'sports',
            'event_description': 'Test bet'
        }), headers=self.headers, content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['bet']['amount'], 0.1)
        self.assertEqual(data['bet']['odds'], 2.5)
    
    def test_create_bet_insufficient_balance(self):
        """Test creating a bet with insufficient balance"""
        response = self.client.post('/api/bets', data=json.dumps({
            'amount': 10.0,
            'odds': 2.5,
            'bet_type': 'sports',
            'event_description': 'Test bet'
        }), headers=self.headers, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)

class PaymentTestCase(APITestCase):
    """Test payment endpoints"""
    
    def setUp(self):
        """Set up test case with registered user"""
        super().setUp()
        response = self.register('testuser', 'test@example.com', 'password123')
        data = json.loads(response.data)
        self.token = data['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    def test_get_wallet(self):
        """Test getting user wallet"""
        response = self.client.get('/api/payment/wallet', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('wallet', data)
        self.assertIn('bitcoin_address', data['wallet'])
    
    def test_get_balance(self):
        """Test getting user balance"""
        response = self.client.get('/api/payment/balance', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['currency'], 'USD')

if __name__ == '__main__':
    unittest.main()
