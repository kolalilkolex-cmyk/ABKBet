"""
Currency conversion utilities for BTC <-> USD
"""

from flask import current_app

def btc_to_usd(btc_amount):
    """Convert BTC amount to USD"""
    rate = current_app.config.get('BTC_TO_USD', 45000.0)
    return btc_amount * rate

def usd_to_btc(usd_amount):
    """Convert USD amount to BTC"""
    rate = current_app.config.get('BTC_TO_USD', 45000.0)
    return usd_amount / rate

def format_usd(usd_amount):
    """Format amount as USD string"""
    return f"${usd_amount:,.2f}"

def format_btc(btc_amount):
    """Format amount as BTC string"""
    return f"₿{btc_amount:.8f}"

def get_exchange_rate():
    """Get current BTC/USD exchange rate"""
    return current_app.config.get('BTC_TO_USD', 45000.0)
