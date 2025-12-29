#!/usr/bin/env python
"""
CLI tool for testing Bitcoin operations
"""

import sys
from app.services.bitcoin_service import BitcoinService

def test_bitcoin():
    """Test Bitcoin operations"""
    btc_service = BitcoinService(network='testnet')
    
    print("Bitcoin Service Tester")
    print("=" * 50)
    
    # Generate address
    print("\n1. Generating new Bitcoin address...")
    try:
        address = btc_service.generate_address()
        print(f"   Address: {address}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Get fee estimates
    print("\n2. Getting fee estimates...")
    try:
        fees = btc_service.get_fee_estimate()
        print(f"   Slow: {fees['slow']} BTC")
        print(f"   Standard: {fees['standard']} BTC")
        print(f"   Fast: {fees['fast']} BTC")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Get address balance (example)
    print("\n3. Getting address balance (using example address)...")
    try:
        # This would require a valid address with history
        balance = btc_service.get_address_balance("mkHS86cQpMH6YJLNVLSLG36L7rNB1rq2j3")
        print(f"   Balance: {balance} BTC")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == '__main__':
    test_bitcoin()
