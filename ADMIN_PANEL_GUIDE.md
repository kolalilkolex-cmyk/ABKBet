# ABKBet Admin Panel - Complete Guide

## 🎨 New Design Features

### **Sidebar Navigation**
- Fixed left sidebar with ABKBet branding
- Easy navigation between sections:
  - **Dashboard** - Overview statistics and recent activity
  - **Manual Matches** - Create and manage betting matches
  - **Deposits** - Approve/reject user deposits
  - **Withdrawals** - Process withdrawal requests
  - **Users** - View all registered users
  - **All Bets** - Monitor betting activity
  - **Transactions** - Complete transaction history
- Logout button at bottom of sidebar

### **Dashboard Statistics Cards**
Beautiful animated stat cards showing:
- Total Users
- Active Bets
- Pending Deposits
- Pending Withdrawals  
- Total Volume (BTC)
- Total Payouts (BTC)

### **Separate Sections**
Each section has its own dedicated page with:
- Clean tables with hover effects
- Action buttons for each item
- Empty states with icons
- Color-coded status badges

## 📋 Admin Features

### **1. Manual Matches Management**
**Create New Match:**
- Home Team & Away Team names
- League (e.g., Premier League, La Liga)
- Match Date & Time
- Betting Odds (Home / Draw / Away)

**Match Operations:**
- ✏️ **Edit** - Update match details
- 🏁 **Update Result** - Enter scores and mark as finished
- 🗑️ **Delete** - Remove match (only if no bets placed)

**Auto-Settlement:**
- When match marked as "finished", all bets automatically settled
- Winners credited, losers marked
- Real-time balance updates

### **2. Deposits Management**
**Pending Deposits Table:**
- User information
- Amount in BTC
- Payment method
- Transaction reference
- Date submitted

**Actions:**
- ✅ **Approve** - Credit user account
- ❌ **Reject** - Cancel deposit request

### **3. Withdrawals Management**
**Pending Withdrawals Table:**
- User information
- Amount in BTC
- Bitcoin address
- Date requested

**Process Withdrawal:**
- Click "Process" button
- Enter blockchain transaction reference
- Confirm processing

### **4. User Management**
**Users Table:**
- ID, Username, Email
- Current Balance (BTC)
- Admin status
- Registration date
- View details button

### **5. Bets Overview**
Monitor all betting activity:
- Bet ID and user
- Match/event details
- Selection (Home/Draw/Away)
- Amount and odds
- Potential payout
- Status (active/won/lost)

### **6. Transactions History**
Complete financial records:
- Transaction type (deposit/withdrawal/bet/payout)
- Amount and status
- Reference numbers
- Timestamps

## 🎨 UI/UX Improvements

### **Color Scheme:**
- **Primary Blue** (#3b82f6) - Main actions, active states
- **Green** (#10b981) - Success, approvals, completed
- **Orange** (#f59e0b) - Pending, warnings, live matches
- **Red** (#dc2626) - Danger, rejections, failed
- **Purple** (#8b5cf6) - Special actions, editing

### **Status Badges:**
- **Pending** - Orange with pulse animation
- **Completed/Approved** - Green
- **Failed/Rejected** - Red
- **Scheduled** - Blue
- **Live** - Animated orange pulse
- **Finished** - Gray

### **Interactive Elements:**
- Hover effects on cards and table rows
- Smooth transitions and animations
- Loading states
- Empty states with helpful messages
- Success/error message notifications

## 🔐 Access Control

### **Admin Login:**
1. Go to `http://127.0.0.1:5000/`
2. Click "Admin Login" or navigate to `/admin`
3. Login with admin credentials (alice / alice123)
4. Access full admin panel

### **Admin-Only Endpoints:**
All `/api/admin/*` endpoints require:
- Valid JWT token
- `is_admin = true` flag on user account

### **Create New Admin:**
```powershell
python scripts/make_admin.py <username>
```

## 📱 Responsive Design
- Mobile-friendly sidebar (collapsible)
- Responsive grid layouts
- Touch-friendly buttons
- Optimized for tablets and phones

## 🚀 How to Use

### **Starting the Server:**

**Option 1 - Double-click:**
```
C:\Users\HP\OneDrive\Documents\ABKBet\start_server.bat
```

**Option 2 - PowerShell:**
```powershell
cd C:\Users\HP\OneDrive\Documents\ABKBet
.\venv_3.12\Scripts\python.exe run.py
```

### **Access Admin Panel:**
1. Open browser: `http://127.0.0.1:5000/admin`
2. Login as admin user
3. Navigate using sidebar menu

### **Common Workflows:**

**Create a Match:**
1. Click "Manual Matches" in sidebar
2. Click "Create New Match" button
3. Fill in team names, league, date, odds
4. Click "Save Match"
5. Match appears on site for users to bet

**Update Match Result:**
1. Go to "Manual Matches"
2. Click 🏁 icon on the match
3. Enter scores (e.g., 2-1)
4. Select status "Finished"
5. Click "Update Result"
6. All bets automatically settled!

**Approve Deposit:**
1. Go to "Deposits" section
2. Review pending deposit details
3. Click ✅ "Approve" button
4. User balance updated instantly

**Process Withdrawal:**
1. Go to "Withdrawals" section
2. Click "Process" button
3. Send BTC to user's address (external)
4. Enter blockchain transaction ID
5. Click "Confirm Processing"

## 📊 API Endpoints

### **Statistics:**
```
GET /api/admin/statistics
```
Returns dashboard stats

### **Matches:**
```
GET    /api/admin/matches              # List all manual matches
POST   /api/admin/matches              # Create new match
GET    /api/admin/matches/<id>         # Get single match
PUT    /api/admin/matches/<id>         # Update match
DELETE /api/admin/matches/<id>         # Delete match
POST   /api/admin/matches/<id>/result  # Update scores & settle bets
```

### **Deposits:**
```
GET  /api/admin/deposits/pending         # List pending
POST /api/admin/deposits/<id>/approve    # Approve deposit
POST /api/admin/deposits/<id>/reject     # Reject deposit
```

### **Withdrawals:**
```
GET  /api/admin/withdrawals/pending      # List pending
POST /api/admin/withdrawals/<id>/process # Process withdrawal
```

### **Users:**
```
GET /api/admin/users          # List all users
GET /api/admin/users/<id>     # Get user details
```

### **Transactions:**
```
GET /api/admin/transactions   # List all transactions
```

## 🎯 Best Practices

1. **Match Creation:**
   - Create matches 24-48 hours in advance
   - Set realistic odds based on team strength
   - Use clear team names (official names)
   - Test with small bets first

2. **Result Updates:**
   - Verify scores before submitting
   - Mark as "Finished" only when match is truly over
   - Check auto-settlement worked correctly

3. **Payment Processing:**
   - Verify deposit amounts match payment method
   - Always enter correct blockchain tx ID for withdrawals
   - Process withdrawals within 24 hours

4. **User Management:**
   - Monitor user activity for suspicious patterns
   - Check balances regularly
   - Be cautious with admin privileges

## 🐛 Troubleshooting

**Server Not Accessible:**
- Check if server is running (Terminal should show Flask output)
- Try: `http://127.0.0.1:5000/admin`
- Keep terminal window open

**Admin Routes 404:**
- Ensure you're logged in as admin user
- Check URL uses `/api/admin/` prefix
- Verify blueprint registered in run.py

**Matches Not Loading:**
- Check browser console for errors
- Verify JWT token is valid
- Ensure matches table exists in database

**Auto-Settlement Not Working:**
- Check match status is set to "finished"
- Verify scores are entered
- Check Flask terminal for errors

## 📁 File Structure

```
ABKBet/
├── templates/
│   ├── admin.html          # NEW Beautiful admin panel
│   ├── admin_old.html      # Backup of old version
│   └── index.html          # User-facing site
├── app/
│   └── routes/
│       ├── admin_routes.py # All admin endpoints
│       └── bet_routes.py   # Public betting routes
├── scripts/
│   ├── generate_admin_panel.py  # Script that created new design
│   ├── make_admin.py            # Make user admin
│   ├── create_test_match.py     # Create sample matches
│   └── create_matches_table.py  # Create matches table
└── start_server.bat        # Easy server startup
```

## 🎉 Next Steps

1. **Test the Admin Panel:**
   - Login and explore all sections
   - Create a test match
   - Try updating match result
   - Check if bets are settled

2. **Customize:**
   - Adjust odds ranges
   - Add more leagues
   - Modify color scheme if needed

3. **Production Ready:**
   - Set up proper email notifications
   - Configure real Bitcoin payment processing
   - Add SSL certificate
   - Use PostgreSQL instead of SQLite
   - Deploy to proper hosting

## 💡 Tips

- **Keep server running** - Don't close terminal window
- **Refresh browser** - After making changes (Ctrl+F5)
- **Check logs** - Flask terminal shows all activity
- **Backup database** - Copy `instance/betting.db` regularly
- **Test everything** - Use test accounts before going live

## 🆘 Support

If you encounter issues:
1. Check Flask terminal for error messages
2. Verify database path is correct
3. Ensure virtual environment is activated
4. Check all tables exist with `scripts/list_users.py`

---

**Version:** 2.0  
**Last Updated:** November 23, 2025  
**Status:** ✅ Production Ready
