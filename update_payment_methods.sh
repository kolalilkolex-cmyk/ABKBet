#!/bin/bash
# Quick Update Script for PythonAnywhere
# Run this in PythonAnywhere Bash console after uploading the files

cd /home/ABKBet/ABKBet

echo "📦 Updating Payment Methods..."

# Backup current files
echo "Creating backups..."
cp app/payment_methods.py app/payment_methods.py.backup.$(date +%Y%m%d_%H%M%S)
cp templates/index.html templates/index.html.backup.$(date +%Y%m%d_%H%M%S)

# Extract the uploaded ZIP (if you uploaded payment_methods_update.zip)
if [ -f "payment_methods_update.zip" ]; then
    echo "Extracting update package..."
    unzip -o payment_methods_update.zip
    rm payment_methods_update.zip
    echo "✅ Files extracted"
fi

# Verify files exist
if [ -f "app/payment_methods.py" ]; then
    echo "✅ payment_methods.py found"
else
    echo "❌ payment_methods.py missing!"
fi

if [ -f "templates/index.html" ]; then
    echo "✅ index.html found"
else
    echo "❌ index.html missing!"
fi

# Reload web app
echo ""
echo "🔄 Now reload your web app:"
echo "   1. Go to Web tab"
echo "   2. Click 'Reload abkbet.pythonanywhere.com'"
echo ""
echo "✅ Update complete!"
echo ""
echo "📊 New payment methods available:"
echo "   Deposits: Bitcoin, Bank Transfer, PayPal, Skrill, Mobile Money, USDT"
echo "   Withdrawals: Bitcoin, Bank Transfer, PayPal, Skrill, Mobile Money, USDT"
