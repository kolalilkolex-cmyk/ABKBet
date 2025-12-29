#!/bin/bash
# Fix API URL in abkbet-client.js for PythonAnywhere deployment

cd ~/static

# Backup original file
cp abkbet-client.js abkbet-client.js.backup

# Replace the hardcoded URL with relative URL
sed -i 's|const currentHost = window.location.hostname;||g' abkbet-client.js
sed -i 's|const currentPort = window.location.port || '\''5000'\'';||g' abkbet-client.js
sed -i 's|baseURL = `http://${currentHost}:${currentPort}/api`;|baseURL = '\''/api'\'';|g' abkbet-client.js

echo "✅ Fixed API URL in abkbet-client.js"
echo "📋 Backup saved as abkbet-client.js.backup"
echo ""
echo "Next steps:"
echo "1. Go to Web tab in PythonAnywhere"
echo "2. Click the green 'Reload' button"
echo "3. Refresh your browser"
