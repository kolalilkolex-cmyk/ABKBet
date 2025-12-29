#!/bin/bash
# Final Fix Deployment Script for ABKBet
# Fixes all issues: payment methods, matches, database errors

cd /home/ABKBet/ABKBet

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "🔧  ABKBet Final Fix Deployment"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Check if fix package exists
if [ ! -f "abkbet_final_fix.zip" ]; then
    echo "❌ Error: abkbet_final_fix.zip not found!"
    echo "   Please upload the ZIP file to /home/ABKBet/ABKBet first"
    exit 1
fi

# Backup current files
echo "🔒 Creating backups..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
cp app/payment_methods.py backups/payment_methods.py.$TIMESTAMP 2>/dev/null
cp templates/index.html backups/index.html.$TIMESTAMP 2>/dev/null
echo "   ✓ Backups saved to backups/ folder"
echo ""

# Extract files
echo "📂 Extracting update files..."
unzip -o abkbet_final_fix.zip
rm abkbet_final_fix.zip
echo "   ✓ Files extracted"
echo ""

# Activate virtual environment
echo "🐍 Activating Python environment..."
workon abkbet_env

# Run the fix script
echo ""
echo "🔧 Running fix script..."
echo "───────────────────────────────────────────────────────────────────"
python fix_all_issues.py

# Check if script succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "✅  ALL FIXES APPLIED SUCCESSFULLY!"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "🔄 FINAL STEP: Reload Web App"
    echo ""
    echo "   1. Go to PythonAnywhere Web tab"
    echo "   2. Click the big green 'Reload' button"
    echo "   3. Wait for reload to complete (~10 seconds)"
    echo ""
    echo "🧪 Then Test Your Site:"
    echo ""
    echo "   Admin Panel (Payment Methods):"
    echo "   → https://abkbet.pythonanywhere.com/secure-admin-access-2024"
    echo "   → Login: admin / admin123"
    echo "   → Check Payment Methods section (should show 6 methods)"
    echo ""
    echo "   User Site (Deposits & Matches):"
    echo "   → https://abkbet.pythonanywhere.com"
    echo "   → Login: testuser / test123"
    echo "   → Deposits tab (should show 6 methods)"
    echo "   → Withdrawals tab (should show 6 methods)"
    echo "   → Matches section (should show 5 matches)"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
else
    echo ""
    echo "❌ Fix script encountered errors!"
    echo "   Check the error messages above"
    exit 1
fi
