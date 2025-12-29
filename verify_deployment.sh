#!/bin/bash
# Deployment Verification Script for PythonAnywhere

echo '================================================'
echo 'ABKBET DEPLOYMENT VERIFICATION'
echo '================================================'
echo ''

# Check if files exist
echo 'Checking template files...'
if [ -f templates/index.html ]; then
    echo ' index.html exists'
else
    echo ' index.html MISSING!'
fi

if [ -f templates/admin.html ]; then
    echo ' admin.html exists'
else
    echo ' admin.html MISSING!'
fi

if [ -f templates/terms.html ]; then
    echo ' terms.html exists'
else
    echo ' terms.html MISSING!'
fi

echo ''
echo 'Checking for USD conversions in admin.html...'
if grep -q 'const BTC_USD = 45000' templates/admin.html; then
    echo ' BTC_USD conversion found'
else
    echo ' BTC_USD conversion MISSING!'
fi

if grep -q '\$\' templates/admin.html; then
    echo ' USD balance display found'
else
    echo ' USD balance display MISSING!'
fi

echo ''
echo 'Checking index.html for contact tab removal...'
if grep -q 'id=\"contactTab\"' templates/index.html; then
    echo ' Contact tab still present in HTML!'
else
    echo ' Contact tab removed from navigation'
fi

if grep -q \"contactTab\").style.display = 'inline-block'\" templates/index.html; then
    echo ' Contact tab logic still in JavaScript!'
else
    echo ' Contact tab logic removed'
fi

echo ''
echo 'Checking footer Contact Support link...'
if grep -q 'onclick=\"switchTab(\047contact\047)\"' templates/index.html; then
    echo ' Contact Support opens modal correctly'
else
    echo ' Contact Support link incorrect!'
fi

echo ''
echo '================================================'
echo 'DEPLOYMENT VERIFICATION COMPLETE'
echo '================================================'
