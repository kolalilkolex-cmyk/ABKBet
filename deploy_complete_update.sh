#!/bin/bash
# Complete Update Script for ABKBet on PythonAnywhere
# Includes: Payment Methods Update + Sample Matches Script

cd /home/ABKBet/ABKBet

echo "📦 ABKBet Complete Update"
echo "========================="
echo ""

# Backup current files
echo "🔒 Creating backups..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp app/payment_methods.py app/payment_methods.py.backup.$TIMESTAMP 2>/dev/null
cp templates/index.html templates/index.html.backup.$TIMESTAMP 2>/dev/null

# Extract update package
if [ -f "abkbet_complete_update.zip" ]; then
    echo "📂 Extracting update package..."
    unzip -o abkbet_complete_update.zip
    rm abkbet_complete_update.zip
    echo "✅ Files extracted"
else
    echo "❌ Update package not found!"
    echo "   Please upload 'abkbet_complete_update.zip' to /home/ABKBet/ABKBet first"
    exit 1
fi

echo ""
echo "📋 Verifying files..."

# Verify files
FILES_OK=true

if [ -f "app/payment_methods.py" ]; then
    echo "✅ app/payment_methods.py"
else
    echo "❌ app/payment_methods.py missing!"
    FILES_OK=false
fi

if [ -f "templates/index.html" ]; then
    echo "✅ templates/index.html"
else
    echo "❌ templates/index.html missing!"
    FILES_OK=false
fi

if [ -f "add_sample_matches.py" ]; then
    echo "✅ add_sample_matches.py"
else
    echo "❌ add_sample_matches.py missing!"
    FILES_OK=false
fi

if [ "$FILES_OK" = false ]; then
    echo ""
    echo "❌ Some files are missing. Update incomplete."
    exit 1
fi

echo ""
echo "🎮 Adding sample matches..."
workon abkbet_env
python add_sample_matches.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Update Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔄 FINAL STEP: Reload Web App"
echo "   1. Go to Web tab on PythonAnywhere"
echo "   2. Click 'Reload abkbet.pythonanywhere.com'"
echo ""
echo "📊 What's New:"
echo "   ✅ All 6 payment methods (deposits + withdrawals)"
echo "   ✅ PayPal & Skrill added to withdrawals"
echo "   ✅ 5 sample matches added for testing"
echo ""
echo "🧪 Test Your Site:"
echo "   https://abkbet.pythonanywhere.com"
echo ""
echo "🎯 Next Steps:"
echo "   1. Login as testuser/test123"
echo "   2. View matches and place test bets"
echo "   3. Test deposit requests (all 6 methods)"
echo "   4. Test withdrawal requests (all 6 methods)"
echo "   5. Login to admin panel to approve requests"
echo ""
