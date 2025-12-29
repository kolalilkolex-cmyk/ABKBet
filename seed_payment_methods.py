"""
Seed all payment methods to the database
Adds all 6 payment methods (Bitcoin, Bank Transfer, PayPal, Skrill, USDT, Mobile Money)
"""
from app import create_app, db
from app.models.payment_method import PaymentMethod
from datetime import datetime

def seed_all_payment_methods():
    """Add or update all payment methods"""
    app = create_app('production')
    
    with app.app_context():
        print("📦 Seeding Payment Methods...")
        print("="*60)
        
        # Define all 6 payment methods
        payment_methods = [
            {
                'method_type': 'bitcoin',
                'method_name': 'Bitcoin (BTC)',
                'wallet_address': 'tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
                'instructions': 'Send BTC to the address above. Minimum deposit: 0.001 BTC. Include your username in the transaction note.',
                'is_active': True
            },
            {
                'method_type': 'usdt',
                'method_name': 'USDT (Tether)',
                'wallet_address': 'TRC20: TXYZabcdef123456789',
                'instructions': 'Send USDT (TRC20 network) to the address above. Make sure to use TRC20 network only. Minimum: 10 USDT.',
                'is_active': True
            },
            {
                'method_type': 'bank_transfer',
                'method_name': 'Bank Transfer',
                'account_name': 'ABKBet Limited',
                'account_number': '1234567890',
                'bank_name': 'Sample Bank',
                'swift_code': 'SAMPNG01',
                'instructions': 'Transfer to the bank account above. Use your username as the reference. Available for Nigerian banks.',
                'is_active': True
            },
            {
                'method_type': 'paypal',
                'method_name': 'PayPal',
                'email': 'payments@abkbet.com',
                'instructions': 'Send payment to the PayPal email above. Add your username in the payment note. Minimum: $10 USD.',
                'is_active': True
            },
            {
                'method_type': 'skrill',
                'method_name': 'Skrill',
                'email': 'payments@abkbet.com',
                'instructions': 'Send payment to the Skrill email above. Add your username in the payment note. Minimum: $10 USD.',
                'is_active': True
            },
            {
                'method_type': 'mobile_money',
                'method_name': 'MTN Mobile Money',
                'phone': '+1234567890',
                'instructions': 'Send Mobile Money to the phone number above. Use your username as reference. MTN network only.',
                'is_active': True
            }
        ]
        
        added_count = 0
        updated_count = 0
        
        for method_data in payment_methods:
            # Check if method already exists
            existing = PaymentMethod.query.filter_by(
                method_type=method_data['method_type']
            ).first()
            
            if existing:
                # Update existing method
                existing.method_name = method_data['method_name']
                existing.wallet_address = method_data.get('wallet_address')
                existing.account_name = method_data.get('account_name')
                existing.account_number = method_data.get('account_number')
                existing.bank_name = method_data.get('bank_name')
                existing.swift_code = method_data.get('swift_code')
                existing.email = method_data.get('email')
                existing.phone = method_data.get('phone')
                existing.instructions = method_data['instructions']
                existing.is_active = method_data['is_active']
                existing.updated_at = datetime.utcnow()
                
                print(f"✓ Updated: {method_data['method_name']}")
                updated_count += 1
            else:
                # Create new method
                new_method = PaymentMethod(
                    method_type=method_data['method_type'],
                    method_name=method_data['method_name'],
                    wallet_address=method_data.get('wallet_address'),
                    account_name=method_data.get('account_name'),
                    account_number=method_data.get('account_number'),
                    bank_name=method_data.get('bank_name'),
                    swift_code=method_data.get('swift_code'),
                    email=method_data.get('email'),
                    phone=method_data.get('phone'),
                    instructions=method_data['instructions'],
                    is_active=method_data['is_active']
                )
                db.session.add(new_method)
                print(f"✓ Added: {method_data['method_name']}")
                added_count += 1
        
        db.session.commit()
        
        print("="*60)
        print(f"✅ Seeding Complete!")
        print(f"   • Added: {added_count} new methods")
        print(f"   • Updated: {updated_count} existing methods")
        print(f"   • Total: {added_count + updated_count} payment methods")
        print("="*60)
        
        # Display all active payment methods
        print("\n📋 Active Payment Methods:")
        all_methods = PaymentMethod.query.filter_by(is_active=True).all()
        for i, method in enumerate(all_methods, 1):
            print(f"   {i}. {method.method_name} ({method.method_type})")
        
        print("\n🎯 Next Steps:")
        print("   1. Reload your web app")
        print("   2. Visit admin panel → Payment Methods")
        print("   3. Update payment details (wallet addresses, emails, etc.)")
        print("   4. Test deposits and withdrawals")

if __name__ == '__main__':
    seed_all_payment_methods()
