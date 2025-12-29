import requests
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BitcoinService:
    """Service for Bitcoin operations"""
    
    def __init__(self, network: str = 'testnet'):
        self.network = network
        self.base_url = self._get_base_url()
        self.api_key = None  # Set your BlockCypher or similar API key
    
    def _get_base_url(self) -> str:
        """Get base URL based on network"""
        if self.network == 'testnet':
            return 'https://testnet.blockexplorer.com/api'
        else:
            return 'https://blockexplorer.com/api'
    
    def generate_address(self) -> str:
        """Generate a new Bitcoin address"""
        try:
            # Try using bit library first
            import bit
            if self.network == 'testnet':
                key = bit.PrivateKeyTestnet()
            else:
                key = bit.PrivateKey()
            return key.address
        except (ImportError, ModuleNotFoundError) as e:
            # Fallback: Generate a mock testnet address for development
            import hashlib
            import os
            logger.warning(f"bit library not available ({e.__class__.__name__}), generating mock address")
            random_bytes = os.urandom(20)
            hash_hex = hashlib.sha256(random_bytes).hexdigest()[:34]
            # Testnet addresses start with 'm' or 'n'
            if self.network == 'testnet':
                return f"n{hash_hex}"
            else:
                return f"1{hash_hex}"
        except Exception as e:
            logger.error(f"Error generating Bitcoin address: {e}")
            # Generate a simple mock address as last resort
            import hashlib
            import os
            random_bytes = os.urandom(20)
            hash_hex = hashlib.sha256(random_bytes).hexdigest()[:34]
            return f"n{hash_hex}" if self.network == 'testnet' else f"1{hash_hex}"
    
    def get_private_key(self) -> str:
        """Generate a new Bitcoin private key"""
        try:
            import bit
            key = bit.PrivateKey()
            return key.to_hex()
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"bit library not available ({e.__class__.__name__}), generating mock private key")
            # Generate a mock 64-character hex string for development
            import hashlib
            import os
            random_bytes = os.urandom(32)
            return hashlib.sha256(random_bytes).hexdigest()
        except Exception as e:
            logger.error(f"Error generating private key: {e}")
            # Return mock key as fallback
            import hashlib
            import os
            random_bytes = os.urandom(32)
            return hashlib.sha256(random_bytes).hexdigest()
    
    def get_address_balance(self, address: str) -> float:
        """Get balance of a Bitcoin address in BTC"""
        try:
            url = f"{self.base_url}/addr/{address}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Convert from satoshis to BTC
            return data.get('balance', 0) / 100000000
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching address balance: {e}")
            return 0.0
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction details"""
        try:
            url = f"{self.base_url}/tx/{tx_hash}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching transaction: {e}")
            return None
    
    def get_address_transactions(self, address: str) -> List[Dict]:
        """Get all transactions for an address"""
        try:
            url = f"{self.base_url}/addr/{address}/full"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('txs', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching address transactions: {e}")
            return []
    
    def verify_transaction(self, tx_hash: str, expected_amount: float, 
                          expected_address: str, required_confirmations: int = 1) -> bool:
        """Verify a transaction meets requirements"""
        try:
            tx_data = self.get_transaction(tx_hash)
            if not tx_data:
                return False
            
            # Check confirmations
            confirmations = tx_data.get('confirmations', 0)
            if confirmations < required_confirmations:
                return False
            
            # Check if output address received expected amount
            for output in tx_data.get('vout', []):
                addresses = output.get('addresses', [])
                if expected_address in addresses:
                    amount_satoshi = output.get('value', 0)
                    amount_btc = amount_satoshi / 100000000
                    if amount_btc >= expected_amount * 0.99:  # Allow 1% variance
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error verifying transaction: {e}")
            return False
    
    def broadcast_transaction(self, raw_tx: str) -> Optional[str]:
        """Broadcast a raw transaction to the network"""
        try:
            url = f"{self.base_url}/txs/push"
            payload = {'tx': raw_tx}
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('tx', {}).get('hash')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error broadcasting transaction: {e}")
            return None
    
    def get_fee_estimate(self) -> Dict[str, float]:
        """Get current Bitcoin network fee estimates"""
        try:
            url = "https://bitcoinfees.earn.com/api/v1/fees/recommended"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'slow': data.get('slowFee', 1) / 100,  # Convert to BTC
                'standard': data.get('halfHourFee', 2) / 100,
                'fast': data.get('fastFee', 3) / 100
            }
        except Exception as e:
            logger.error(f"Error fetching fee estimate: {e}")
            return {'slow': 0.0001, 'standard': 0.0002, 'fast': 0.0003}
