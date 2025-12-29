# Deposit Approval System - Implementation Guide

## What Changed:

### Backend:
1. **New Model**: `DepositRequest` - stores deposit requests pending admin approval
2. **New Routes**: `/api/deposit/*` - handles deposit workflow
3. **Payment Config**: `config/payment_methods.py` - stores payment details

### Frontend Changes Needed:
1. Update deposit form to show payment details BEFORE submission
2. Add deposit status tracking for users
3. Add admin panel section for approving/rejecting deposits

## Workflow:

### User Side:
1. User clicks "Deposit"
2. Selects payment method → Shows payment details (address, bank account, etc.)
3. User makes payment externally
4. User submits transaction reference/proof
5. User sees "Pending approval" status
6. Admin approves → Balance credited instantly

### Admin Side:
1. Admin sees list of pending deposits
2. Admin clicks "Approve" or "Reject"
3. If approved: User balance updated automatically
4. User notified via status change

## Setup Steps:

1. **Update payment details** in `config/payment_methods.py`:
   - Add your real Bitcoin address
   - Add your bank account details
   - Add PayPal/Skrill emails

2. **Create database table**:
   ```bash
   python scripts/create_deposit_table.py
   ```

3. **Update frontend** (I'll provide the code next)

4. **Test the flow**:
   - Register as user
   - Submit deposit request
   - Login as admin
   - Approve deposit
   - Check user balance

## API Endpoints:

### User Endpoints:
- `GET /api/deposit/methods` - Get available payment methods
- `GET /api/deposit/method/{id}` - Get specific payment method details
- `POST /api/deposit/request` - Submit deposit request
- `GET /api/deposit/my-requests` - View my deposit history

### Admin Endpoints:
- `GET /api/deposit/pending` - Get all pending deposits
- `GET /api/deposit/all?status=pending` - Filter deposits by status
- `POST /api/deposit/approve/{id}` - Approve deposit
- `POST /api/deposit/reject/{id}` - Reject deposit

## Next Steps:

Would you like me to:
1. Update the frontend deposit UI now?
2. Create the admin approval panel?
3. Both?
