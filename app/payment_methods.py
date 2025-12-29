"""Payment method configuration - Update with your actual payment details"""

PAYMENT_METHODS = {
    'bitcoin': {
        'name': 'Bitcoin (BTC)',
        'enabled': True,
        'details': {
            'address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',  # Replace with your Bitcoin address
            'network': 'Bitcoin Mainnet',
            'min_confirmations': 1,
            'processing_time': '10-30 minutes'
        },
        'instructions': [
            'Send Bitcoin to the address shown above',
            'Copy the exact amount shown in BTC',
            'Wait for at least 1 confirmation',
            'Enter your transaction hash below',
            'Admin will verify and credit your account'
        ],
        'min_deposit': 10,  # USD
        'max_deposit': 10000  # USD
    },
    'bank_transfer': {
        'name': 'Bank Transfer (Africa)',
        'enabled': True,
        'details': {
            'countries': {
                'nigeria': {
                    'name': 'Nigeria',
                    'available': True,
                    'banks': [
                        {
                            'bank_name': 'GTBank',
                            'account_name': 'ABKBet Limited',
                            'account_number': '0123456789',
                            'sort_code': '058'
                        },
                        {
                            'bank_name': 'Access Bank',
                            'account_name': 'ABKBet Limited',
                            'account_number': '0987654321',
                            'sort_code': '044'
                        },
                        {
                            'bank_name': 'Zenith Bank',
                            'account_name': 'ABKBet Limited',
                            'account_number': '1234567890',
                            'sort_code': '057'
                        },
                        {
                            'bank_name': 'First Bank',
                            'account_name': 'ABKBet Limited',
                            'account_number': '2345678901',
                            'sort_code': '011'
                        },
                        {
                            'bank_name': 'UBA',
                            'account_name': 'ABKBet Limited',
                            'account_number': '3456789012',
                            'sort_code': '033'
                        },
                        {
                            'bank_name': 'OPay',
                            'account_name': 'ABKBet Limited',
                            'account_number': '4567890123',
                            'sort_code': 'OPY'
                        },
                        {
                            'bank_name': 'Moniepoint',
                            'account_name': 'ABKBet Limited',
                            'account_number': '5678901234',
                            'sort_code': 'MNP'
                        },
                        {
                            'bank_name': 'PalmPay',
                            'account_name': 'ABKBet Limited',
                            'account_number': '6789012345',
                            'sort_code': 'PLP'
                        }
                    ]
                },
                'ghana': {'name': 'Ghana', 'available': False},
                'kenya': {'name': 'Kenya', 'available': False},
                'south_africa': {'name': 'South Africa', 'available': False},
                'uganda': {'name': 'Uganda', 'available': False},
                'tanzania': {'name': 'Tanzania', 'available': False},
                'rwanda': {'name': 'Rwanda', 'available': False},
                'ethiopia': {'name': 'Ethiopia', 'available': False},
                'egypt': {'name': 'Egypt', 'available': False},
                'morocco': {'name': 'Morocco', 'available': False},
                'senegal': {'name': 'Senegal', 'available': False},
                'ivory_coast': {'name': 'Ivory Coast', 'available': False},
                'cameroon': {'name': 'Cameroon', 'available': False},
                'zimbabwe': {'name': 'Zimbabwe', 'available': False},
                'zambia': {'name': 'Zambia', 'available': False},
                'botswana': {'name': 'Botswana', 'available': False}
            },
            'processing_time': 'Instant after verification'
        },
        'instructions': [
            'Select your country from the list',
            'Choose your bank (Nigeria only)',
            'Transfer funds to the bank account shown',
            'Use your username as the reference',
            'Enter the transaction reference number below',
            'Admin will verify and credit your account'
        ],
        'min_deposit': 20,
        'max_deposit': 50000
    },
    'paypal': {
        'name': 'PayPal',
        'enabled': True,
        'details': {
            'email': 'payments@abkbet.com',  # Replace with your PayPal email
            'processing_time': 'Instant after verification'
        },
        'instructions': [
            'Send payment to the PayPal email above',
            'Add your username in the payment note',
            'Enter the PayPal transaction ID below',
            'Admin will verify and credit your account'
        ],
        'min_deposit': 10,
        'max_deposit': 5000
    },
    'skrill': {
        'name': 'Skrill',
        'enabled': True,
        'details': {
            'email': 'payments@abkbet.com',  # Replace with your Skrill email
            'processing_time': 'Instant after verification'
        },
        'instructions': [
            'Send payment to the Skrill email above',
            'Add your username in the payment note',
            'Enter the Skrill transaction ID below',
            'Admin will verify and credit your account'
        ],
        'min_deposit': 10,
        'max_deposit': 5000
    },
    'usdt': {
        'name': 'USDT (Tether)',
        'enabled': True,
        'details': {
            'address': '0x1234567890123456789012345678901234567890',  # Replace with your USDT address
            'network': 'TRC20 (Tron)',  # or ERC20 (Ethereum)
            'processing_time': '5-15 minutes'
        },
        'instructions': [
            'Send USDT to the address shown above',
            'Make sure you use the correct network (TRC20)',
            'Enter your transaction hash below',
            'Admin will verify and credit your account'
        ],
        'min_deposit': 10,
        'max_deposit': 10000
    },
    'mobile_money': {
        'name': 'MTN Mobile Money',
        'enabled': True,
        'details': {
            'phone': '+1234567890',  # Replace with your MTN Mobile Money number
            'network': 'MTN',
            'processing_time': 'Instant after verification'
        },
        'instructions': [
            'Send Mobile Money to the phone number shown above',
            'Use your username as the reference',
            'Enter the transaction reference number below',
            'Admin will verify and credit your account'
        ],
        'min_deposit': 10,
        'max_deposit': 10000
    }
}

def get_payment_method(method_id):
    """Get payment method configuration from database"""
    from app.models.payment_method import PaymentMethod
    
    # Try to get from database first
    method = PaymentMethod.query.filter_by(method_type=method_id, is_active=True).first()
    
    if method:
        # Build details dict based on method type
        details = {}
        
        if method_id in ['bitcoin', 'crypto']:
            details = {
                'address': method.wallet_address or 'Not configured',
                'network': 'Bitcoin Mainnet',
                'min_confirmations': 1,
                'processing_time': '10-30 minutes'
            }
        elif method_id == 'usdt':
            details = {
                'address': method.usdt_wallet_address or 'Not configured',
                'network': method.usdt_network or 'TRC20 (Tron)',
                'processing_time': '5-15 minutes'
            }
        elif method_id == 'bank_transfer':
            # For bank transfer, use hardcoded structure for now
            # Admin should configure this via database in future
            details = PAYMENT_METHODS.get('bank_transfer', {}).get('details', {})
        elif method_id in ['paypal', 'skrill']:
            details = {
                'email': method.email or 'Not configured',
                'processing_time': 'Instant after verification'
            }
        elif method_id == 'mobile_money':
            details = {
                'phone': method.phone or 'Not configured',
                'processing_time': '5-15 minutes'
            }
        
        return {
            'name': method.method_name,
            'enabled': method.is_active,
            'details': details,
            'instructions': method.instructions.split('\n') if method.instructions else PAYMENT_METHODS.get(method_id, {}).get('instructions', []),
            'min_deposit': 10,  # Could add these to PaymentMethod model
            'max_deposit': 10000
        }
    
    # Fallback to hardcoded if not in database
    return PAYMENT_METHODS.get(method_id)

def get_enabled_payment_methods():
    """Get all enabled payment methods from database"""
    from app.models.payment_method import PaymentMethod
    
    # Get from database
    db_methods = PaymentMethod.query.filter_by(is_active=True).all()
    
    if db_methods:
        result = {}
        for method in db_methods:
            method_config = get_payment_method(method.method_type)
            if method_config:
                result[method.method_type] = method_config
        return result
    
    # Fallback to hardcoded if database empty
    return {k: v for k, v in PAYMENT_METHODS.items() if v.get('enabled', False)}

# Withdrawal method configuration (same as deposits but with withdrawal-specific limits)
WITHDRAWAL_METHODS = {
    'bitcoin': {
        'name': 'Bitcoin (BTC)',
        'enabled': True,
        'details': {
            'network': 'Bitcoin Mainnet',
            'min_confirmations': 1,
            'processing_time': '24-48 hours'
        },
        'instructions': [
            'Enter your Bitcoin wallet address',
            'Ensure the address is correct (irreversible)',
            'Withdrawals are processed manually',
            'You will receive payment within 24-48 hours',
            'Check your wallet for confirmation'
        ],
        'min_withdrawal': 20,  # USD
        'max_withdrawal': 50000  # USD
    },
    'bank_transfer': {
        'name': 'Bank Transfer (Africa)',
        'enabled': True,
        'details': {
            'countries': {
                'nigeria': {
                    'name': 'Nigeria',
                    'available': True
                },
                'ghana': {'name': 'Ghana', 'available': False},
                'kenya': {'name': 'Kenya', 'available': False},
                'south_africa': {'name': 'South Africa', 'available': False},
                'uganda': {'name': 'Uganda', 'available': False},
                'tanzania': {'name': 'Tanzania', 'available': False},
                'rwanda': {'name': 'Rwanda', 'available': False},
                'ethiopia': {'name': 'Ethiopia', 'available': False},
                'egypt': {'name': 'Egypt', 'available': False},
                'morocco': {'name': 'Morocco', 'available': False},
                'senegal': {'name': 'Senegal', 'available': False},
                'ivory_coast': {'name': 'Ivory Coast', 'available': False},
                'cameroon': {'name': 'Cameroon', 'available': False},
                'zimbabwe': {'name': 'Zimbabwe', 'available': False},
                'zambia': {'name': 'Zambia', 'available': False},
                'botswana': {'name': 'Botswana', 'available': False}
            },
            'processing_time': 'Instant after verification'
        },
        'instructions': [
            'Select your country from the list',
            'Enter your bank details (name, account number)',
            'Provide your full account name',
            'Withdrawals are verified and processed manually',
            'Funds will be sent to your account within 24 hours'
        ],
        'min_withdrawal': 20,
        'max_withdrawal': 50000
    },
    'paypal': {
        'name': 'PayPal',
        'enabled': True,
        'details': {
            'processing_time': '24-48 hours'
        },
        'instructions': [
            'Enter your PayPal email address',
            'Ensure the email is correct',
            'Withdrawals are processed manually',
            'You will receive payment within 24-48 hours',
            'Check your PayPal account for confirmation'
        ],
        'min_withdrawal': 10,
        'max_withdrawal': 5000
    },
    'skrill': {
        'name': 'Skrill',
        'enabled': True,
        'details': {
            'processing_time': '24-48 hours'
        },
        'instructions': [
            'Enter your Skrill email address',
            'Ensure the email is correct',
            'Withdrawals are processed manually',
            'You will receive payment within 24-48 hours',
            'Check your Skrill account for confirmation'
        ],
        'min_withdrawal': 10,
        'max_withdrawal': 5000
    },
    'usdt': {
        'name': 'USDT (Tether)',
        'enabled': True,
        'details': {
            'network': 'TRC20 (Tron) or ERC20 (Ethereum)',
            'processing_time': '24-48 hours'
        },
        'instructions': [
            'Enter your USDT wallet address',
            'Specify the network (TRC20 or ERC20)',
            'Ensure the address is correct (irreversible)',
            'Withdrawals are processed manually',
            'You will receive payment within 24-48 hours'
        ],
        'min_withdrawal': 20,
        'max_withdrawal': 50000
    },
    'mobile_money': {
        'name': 'MTN Mobile Money',
        'enabled': True,
        'details': {
            'network': 'MTN',
            'processing_time': '24-48 hours'
        },
        'instructions': [
            'Enter your MTN Mobile Money phone number',
            'Ensure the number is correct',
            'Withdrawals are processed manually',
            'You will receive payment within 24-48 hours',
            'Check your mobile money account for confirmation'
        ],
        'min_withdrawal': 20,
        'max_withdrawal': 50000
    }
}

def get_withdrawal_method(method_id):
    """Get withdrawal method configuration"""
    return WITHDRAWAL_METHODS.get(method_id)

def get_enabled_withdrawal_methods():
    """Get all enabled withdrawal methods"""
    return {k: v for k, v in WITHDRAWAL_METHODS.items() if v.get('enabled', False)}
