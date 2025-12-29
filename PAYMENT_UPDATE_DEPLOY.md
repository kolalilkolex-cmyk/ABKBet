# Payment Management Feature - Deployment Instructions

## 🎉 What's New

This update adds comprehensive admin payment management features:

✅ **View User Payment Information** - See all payment methods for any user  
✅ **Update Payment Details** - Edit wallet addresses, bank accounts, PayPal, etc.  
✅ **Payment Submissions View** - See all deposit/withdrawal requests with payment details  
✅ **Database Fields Added** - 8 new payment-related fields in users table  

## 📦 Package Contents

- **ABKBet_Payment_Management.zip** (481 KB)
- Updated `app/models/__init__.py` - User model with payment fields
- Updated `app/routes/admin_routes.py` - 3 new payment management endpoints
- Updated `templates/admin.html` - Payment info modal and UI
- New `migrations/add_payment_fields.py` - Database migration script
- New `PAYMENT_MANAGEMENT_GUIDE.md` - Complete feature documentation

## 🚀 Deployment Steps

### Step 1: Upload Package
```bash
# On PythonAnywhere console
cd /home/Lilkolex
wget YOUR_UPLOAD_URL/ABKBet_Payment_Management.zip
unzip -o ABKBet_Payment_Management.zip -d ABKBet/
```

Or use "Files" tab to upload and extract manually.

### Step 2: Run Database Migration
```bash
cd /home/Lilkolex/ABKBet
source ~/.virtualenvs/abkbet_env/bin/activate
python migrations/add_payment_fields.py upgrade
```

**Expected Output:**
```
Adding column: withdrawal_wallet
Adding column: bank_account_name
Adding column: bank_account_number
Adding column: bank_name
Adding column: paypal_email
Adding column: skrill_email
Adding column: usdt_wallet
Adding column: payment_notes
✓ Payment fields migration completed successfully
```

### Step 3: Verify Changes
```bash
# Check database has new columns
python check_db.py

# Test imports
python -c "from app.models import User; from app.models.deposit import DepositRequest; print('✓ Models imported successfully')"
```

### Step 4: Reload Web App
```bash
# Touch wsgi.py to reload
touch /var/www/lilkolex_pythonanywhere_com_wsgi.py

# Or use PythonAnywhere "Reload" button in Web tab
```

## 🧪 Testing

### Test 1: View Payment Info
1. Login to admin panel: https://lilkolex.pythonanywhere.com/admin.html
2. Go to "Users" section
3. Click wallet icon (💳) next to any user
4. Should see payment info modal with all fields

### Test 2: Update Payment Info
1. Open payment info modal
2. Fill in some payment details:
   - Bitcoin wallet: `bc1qtest123...`
   - Bank name: `Test Bank`
   - Account number: `1234567890`
3. Click "Save Changes"
4. Should see success message
5. Reopen modal - changes should persist

### Test 3: API Endpoints
```bash
# Get user payment info (replace USER_ID and TOKEN)
curl -X GET "https://lilkolex.pythonanywhere.com/api/admin/users/1/payment-info" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Update payment info
curl -X PUT "https://lilkolex.pythonanywhere.com/api/admin/users/1/payment-info" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "withdrawal_wallet": "bc1qtest...",
    "bank_name": "Test Bank"
  }'

# Get payment submissions
curl -X GET "https://lilkolex.pythonanywhere.com/api/admin/payments/submissions?status=pending" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 📋 Changed Files

1. **app/models/__init__.py**
   - Added 8 payment fields to User model

2. **app/routes/admin_routes.py**
   - Import DepositRequest and JWT functions
   - Added `get_user_payment_info()` endpoint
   - Added `update_user_payment_info()` endpoint
   - Added `get_payment_submissions()` endpoint

3. **templates/admin.html**
   - Added wallet icon button to users table
   - Added payment info modal (700px width)
   - Added `viewPaymentInfo()` function
   - Added `closePaymentInfoModal()` function
   - Added payment form submit handler

4. **migrations/add_payment_fields.py** (NEW)
   - Database migration script
   - Adds 8 columns to users table
   - Supports upgrade/downgrade

5. **PAYMENT_MANAGEMENT_GUIDE.md** (NEW)
   - Complete feature documentation
   - API reference
   - Usage workflow
   - Troubleshooting guide

## 🔐 Security

- All endpoints require admin JWT authentication
- User model fields are nullable (no breaking changes)
- Payment info only visible to admins
- All updates are logged with admin username

## 🐛 Troubleshooting

### Migration fails with "column already exists"
**Solution:** Migration script checks for existing columns and skips them. Safe to re-run.

### "DepositRequest is not defined" error
**Solution:** Import was added to admin_routes.py. Make sure file was updated correctly.

### Payment info modal doesn't open
**Solution:** 
1. Check browser console for errors
2. Verify admin.html was updated
3. Clear browser cache (Ctrl+Shift+R)

### Changes not showing on website
**Solution:**
1. Reload web app in PythonAnywhere
2. Check error logs: `tail -n 50 /var/log/lilkolex.pythonanywhere.com.error.log`
3. Verify files were extracted to correct location

## 📊 Database Schema

**New columns in `users` table:**
```sql
ALTER TABLE users ADD COLUMN withdrawal_wallet VARCHAR(255);
ALTER TABLE users ADD COLUMN bank_account_name VARCHAR(255);
ALTER TABLE users ADD COLUMN bank_account_number VARCHAR(100);
ALTER TABLE users ADD COLUMN bank_name VARCHAR(255);
ALTER TABLE users ADD COLUMN paypal_email VARCHAR(255);
ALTER TABLE users ADD COLUMN skrill_email VARCHAR(255);
ALTER TABLE users ADD COLUMN usdt_wallet VARCHAR(255);
ALTER TABLE users ADD COLUMN payment_notes TEXT;
```

## 📞 Support

If you encounter any issues:

1. Check `/var/log/lilkolex.pythonanywhere.com.error.log`
2. Check `logs/app.log` in ABKBet directory
3. Run `python check_db.py` to verify database state
4. Review `PAYMENT_MANAGEMENT_GUIDE.md` for detailed documentation

## ✅ Rollback (if needed)

To remove payment fields:
```bash
cd /home/Lilkolex/ABKBet
source ~/.virtualenvs/abkbet_env/bin/activate
python migrations/add_payment_fields.py downgrade
```

## 🎯 Next Steps

After successful deployment:

1. ✅ Test all three new endpoints
2. ✅ Add payment info for a few test users
3. ✅ Process a test withdrawal using saved payment details
4. ✅ Check that payment submissions show user details
5. ✅ Read `PAYMENT_MANAGEMENT_GUIDE.md` for advanced usage

---

**Package:** ABKBet_Payment_Management.zip  
**Size:** 481 KB  
**Date:** December 6, 2024  
**Version:** 1.5.0 (Payment Management Update)
