# Admin Panel Guide

## Overview
The ABKBet admin panel provides comprehensive control over the betting platform including payment verification, user management, and bet settlement.

## Access

### Admin URL
Navigate to: `http://127.0.0.1:5000/admin`

### Setting Up Admin Account

1. **Create or use existing account:**
   ```bash
   # Register via the main site or use existing user
   ```

2. **Grant admin privileges:**
   ```bash
   cd C:\Users\HP\OneDrive\Documents\ABKBet
   python scripts/make_admin.py <username>
   ```
   
   Example:
   ```bash
   python scripts/make_admin.py admin
   ```

3. **Login to admin panel:**
   - Navigate to `/admin`
   - Login with your admin credentials
   - You'll see the admin dashboard

## Admin Features

### 1. Dashboard Statistics
Real-time overview of platform metrics:
- **Total Users**: Number of registered users
- **Active Bets**: Currently pending bets
- **Pending Deposits**: Deposits waiting for approval
- **Pending Withdrawals**: Withdrawals to be processed
- **Total Volume**: All-time betting volume (BTC)
- **Total Payouts**: All-time payouts (BTC)

### 2. Deposit Management

**Viewing Pending Deposits:**
- Navigate to "Pending Deposits" tab
- See all deposits waiting for verification
- View: User, Amount, Payment Method, Reference ID, Date

**Approving Deposits:**
1. Review deposit details
2. Verify payment through external system (Skrill, Revolut, etc.)
3. Click "Approve" button
4. User's balance is credited immediately

**Rejecting Deposits:**
1. Click "Reject" for invalid deposits
2. Confirm rejection
3. Transaction marked as failed

### 3. Withdrawal Management

**Processing Withdrawals:**
1. Navigate to "Pending Withdrawals" tab
2. Review withdrawal requests
3. Click "Process" button
4. **Important**: Enter the actual blockchain transaction hash
5. Send Bitcoin to user's address manually via your wallet
6. Submit the transaction hash
7. Withdrawal marked as completed

**Manual Blockchain Transfer:**
```bash
# Use your Bitcoin wallet to send funds
# Then paste the transaction hash into the admin panel
```

### 4. User Management

**View All Users:**
- Navigate to "Users" tab
- See user details: Username, Email, Balance, Join Date
- Click "View" to see detailed user information

**Adjust User Balance (Manual Correction):**
```bash
# Via API (using Postman or similar)
POST /api/admin/users/<user_id>/balance
{
  "amount": 0.001,  // Positive to add, negative to deduct
  "reason": "Bonus credit"
}
```

**User Details Include:**
- Account information
- Betting statistics
- Transaction history
- Wallet details

### 5. Bet Management

**Settle Bets:**
1. Navigate to "Bets" tab
2. View all active bets
3. When event concludes, settle each bet:
   - Click on bet
   - Select "Won" or "Lost"
   - Confirm settlement
4. Winning bets credit user automatically

**Bet Settlement via API:**
```bash
POST /api/admin/bets/<bet_id>/settle
{
  "result": "won"  // or "lost"
}
```

### 6. Transaction Monitoring

**View All Transactions:**
- Navigate to "All Transactions" tab
- Filter by type (deposit/withdrawal) and status
- Monitor all platform financial activity

## Admin Operations Workflow

### Daily Operations

1. **Morning Check:**
   - Review dashboard statistics
   - Check pending deposits
   - Approve/reject as needed

2. **Payment Verification:**
   - **For Deposits:**
     - Login to payment provider (Skrill, Revolut, Eversend)
     - Match transaction reference IDs
     - Verify amounts
     - Approve in admin panel

3. **Withdrawal Processing:**
   - Check pending withdrawals
   - Use your Bitcoin wallet to send funds
   - Copy blockchain transaction hash
   - Complete withdrawal in admin panel

4. **Bet Settlement:**
   - Monitor active bets
   - When games finish, check results
   - Settle bets accordingly
   - Verify user balances updated

### Payment Provider Integration

**Skrill:**
1. Login to merchant account
2. Check transaction history
3. Match reference IDs with pending deposits
4. Verify amounts match
5. Approve in admin panel

**Revolut:**
1. Check business account
2. Verify incoming payments
3. Match reference IDs
4. Approve deposits

**Bitcoin:**
1. Check your Bitcoin wallet for deposits
2. Verify confirmations (at least 1)
3. Match addresses and amounts
4. Process in admin panel

### Security Best Practices

1. **Never share admin credentials**
2. **Verify all transactions before approval**
3. **Double-check withdrawal addresses**
4. **Keep blockchain transaction records**
5. **Monitor for suspicious activity**
6. **Regularly review user statistics**

## API Endpoints

All admin endpoints require authentication and admin privileges.

### Statistics
```
GET /api/admin/statistics
```

### Deposits
```
GET /api/admin/deposits/pending
POST /api/admin/deposits/<id>/approve
POST /api/admin/deposits/<id>/reject
```

### Withdrawals
```
GET /api/admin/withdrawals/pending
POST /api/admin/withdrawals/<id>/process
Body: { "tx_hash": "blockchain_transaction_hash" }
```

### Users
```
GET /api/admin/users?page=1&per_page=20
GET /api/admin/users/<user_id>
POST /api/admin/users/<user_id>/balance
Body: { "amount": 0.001, "reason": "Adjustment reason" }
```

### Bets
```
GET /api/admin/bets?status=pending
POST /api/admin/bets/<bet_id>/settle
Body: { "result": "won" }  // or "lost"
```

### Transactions
```
GET /api/admin/transactions?page=1&type=deposit&status=pending
```

## Troubleshooting

### Can't Access Admin Panel
- Ensure user has `is_admin = True` in database
- Run: `python scripts/make_admin.py <username>`
- Check you're logged in
- Clear browser cache

### Deposits Not Showing
- Check transaction status in database
- Verify payment provider integration
- Review application logs: `logs/run_app.log`

### Withdrawals Stuck
- Ensure blockchain transaction was sent
- Verify transaction hash is correct
- Check Bitcoin network confirmations

### Balance Issues
- Use balance adjustment endpoint
- Verify in database directly
- Check transaction history

## Database Direct Access

If needed, access database directly:

```bash
cd C:\Users\HP\OneDrive\Documents\ABKBet
python
```

```python
from app.models import db, User
from run import create_app

app = create_app()
with app.app_context():
    # Make user admin
    user = User.query.filter_by(username='admin').first()
    user.is_admin = True
    db.session.commit()
    
    # Check admin users
    admins = User.query.filter_by(is_admin=True).all()
    for admin in admins:
        print(f"Admin: {admin.username}")
```

## Support

For issues or questions:
1. Check application logs: `logs/run_app.log`
2. Review database state
3. Verify payment provider integration
4. Test API endpoints with Postman

## Important Notes

⚠️ **Critical Operations:**
- Always verify payment before approving deposits
- Double-check wallet addresses for withdrawals
- Keep records of all blockchain transactions
- Regularly backup the database
- Monitor for fraudulent activity

✅ **Best Practices:**
- Process deposits/withdrawals within 24 hours
- Settle bets immediately after events conclude
- Maintain accurate financial records
- Regularly review platform statistics
- Keep admin credentials secure
