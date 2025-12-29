# Admin Payment Management Guide

## Overview
The admin panel now includes comprehensive payment and withdrawal management features. Admins can view and update user payment information, making transaction processing much easier.

## Features Added

### 1. **View User Payment Information**
- Click the **Wallet icon (💳)** next to any user in the Users table
- View complete payment details including:
  - Bitcoin withdrawal wallet
  - USDT wallet addresses
  - Bank account details
  - PayPal email
  - Skrill email
  - Additional payment notes

### 2. **Update User Payment Information**
- Open payment info modal for any user
- Edit any payment field:
  - **Crypto Wallets**: Bitcoin, USDT addresses
  - **Bank Details**: Account name, bank name, account number
  - **Other Methods**: PayPal, Skrill emails
  - **Notes**: Any additional payment information
- Click "Save Changes" to update

### 3. **View Payment Submissions**
New API endpoint available:
```
GET /api/admin/payments/submissions
```

Parameters:
- `status`: Filter by status (pending, approved, rejected)
- `user_id`: Filter by specific user
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)

Returns all deposit/withdrawal requests with user payment details inline.

## Database Changes

### New User Model Fields
The following fields have been added to the `users` table:

| Field | Type | Description |
|-------|------|-------------|
| `withdrawal_wallet` | VARCHAR(255) | User's Bitcoin withdrawal address |
| `bank_account_name` | VARCHAR(255) | Account holder name |
| `bank_account_number` | VARCHAR(100) | Bank account number |
| `bank_name` | VARCHAR(255) | Bank name |
| `paypal_email` | VARCHAR(255) | PayPal email address |
| `skrill_email` | VARCHAR(255) | Skrill email address |
| `usdt_wallet` | VARCHAR(255) | USDT wallet address (TRC20/ERC20) |
| `payment_notes` | TEXT | Additional payment information |

## Migration

To add the new payment fields to your existing database, run:

```bash
python migrations/add_payment_fields.py upgrade
```

To rollback (remove fields):
```bash
python migrations/add_payment_fields.py downgrade
```

## API Endpoints

### Get User Payment Info
```
GET /api/admin/users/<user_id>/payment-info
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "payment_info": {
    "user_id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "balance": 0.05,
    "withdrawal_wallet": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    "bank_account_name": "John Doe",
    "bank_account_number": "1234567890",
    "bank_name": "Bank of America",
    "paypal_email": "john@paypal.com",
    "skrill_email": "john@skrill.com",
    "usdt_wallet": "TXyz123...",
    "payment_notes": "Prefers BTC on weekends"
  }
}
```

### Update User Payment Info
```
PUT /api/admin/users/<user_id>/payment-info
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "withdrawal_wallet": "bc1qnew_wallet_address",
  "bank_account_name": "John Doe",
  "bank_account_number": "9876543210",
  "bank_name": "Chase Bank",
  "paypal_email": "newemail@paypal.com",
  "skrill_email": "newemail@skrill.com",
  "usdt_wallet": "TNew123...",
  "payment_notes": "Updated payment preferences"
}
```

**Response:**
```json
{
  "message": "Payment information updated successfully",
  "payment_info": { /* updated info */ }
}
```

### Get Payment Submissions
```
GET /api/admin/payments/submissions
Authorization: Bearer <admin_token>

Query Parameters:
- status: pending|approved|rejected
- user_id: <user_id>
- page: <page_number>
- per_page: <items_per_page>
```

**Response:**
```json
{
  "submissions": [
    {
      "id": 1,
      "user_id": 123,
      "amount": 100.00,
      "payment_method": "bank_transfer",
      "transaction_reference": "TXN123456",
      "payment_proof": "/uploads/proof123.jpg",
      "status": "pending",
      "admin_notes": null,
      "created_at": "2024-01-15T10:30:00Z",
      "user_details": {
        "username": "john_doe",
        "email": "john@example.com",
        "balance": 0.05,
        "withdrawal_wallet": "bc1q...",
        "bank_account_name": "John Doe",
        "bank_account_number": "1234567890",
        "bank_name": "Bank of America",
        "paypal_email": "john@paypal.com"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

## Usage Workflow

### Processing Withdrawals
1. User requests withdrawal in the app
2. Admin opens "Withdrawals" section
3. Click wallet icon to view user's saved payment details
4. Process payment to their preferred method
5. Approve withdrawal with transaction reference

### Updating User Payment Info
1. Navigate to "Users" section
2. Find the user and click wallet icon (💳)
3. View current payment information
4. Update any fields as needed
5. Save changes
6. User's payment info is now updated for future transactions

### Managing Deposits
1. User submits deposit with payment details
2. Admin views submission in deposits section
3. Click payment info to see user's complete payment history
4. Approve or reject deposit
5. Add admin notes if needed

## Benefits

✅ **Faster Transaction Processing**: All payment details in one place  
✅ **Better Record Keeping**: Track user preferred payment methods  
✅ **Reduced Errors**: Pre-filled payment information  
✅ **User Convenience**: Users don't need to re-enter payment details  
✅ **Audit Trail**: Payment notes field for admin documentation  

## Security Notes

⚠️ **Important Security Considerations:**

1. **Access Control**: Only admins can view/edit payment information
2. **JWT Required**: All endpoints require valid admin JWT token
3. **Sensitive Data**: Payment info is sensitive - handle with care
4. **Logging**: All payment info updates are logged with admin username
5. **Validation**: Validate wallet addresses and account numbers before saving

## Troubleshooting

### Issue: Payment info not saving
**Solution**: Check that you have admin privileges and valid JWT token

### Issue: Migration fails
**Solution**: 
```bash
# Check if columns exist
python check_db.py

# Run migration again
python migrations/add_payment_fields.py upgrade
```

### Issue: Old users don't have payment fields
**Solution**: Fields are nullable - users can add them via profile settings or admin can add them

## Next Steps

Consider adding:
- User self-service payment info updates
- Payment method verification (email confirmation, wallet validation)
- Payment history tracking per method
- Automated wallet address validation
- Support for more payment providers (Neteller, Payoneer, etc.)

## Support

For issues or questions:
- Check `logs/app.log` for detailed error messages
- Verify database migration completed: `python check_db.py`
- Test endpoints with Postman or curl
- Contact development team for custom payment method integrations
