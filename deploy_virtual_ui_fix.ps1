# Deploy Virtual Games UI Fixes to PythonAnywhere
# This script uploads the fixed files

Write-Host "=== Deploying Virtual Games UI Fixes ===" -ForegroundColor Cyan
Write-Host ""

# Files to upload
$files = @(
    @{
        Local = "app\models\virtual_game.py"
        Remote = "ABKBet/app/models/virtual_game.py"
        Description = "Fixed to_dict() to return null scores for scheduled games"
    },
    @{
        Local = "templates\index.html"
        Remote = "ABKBet/templates/index.html"
        Description = "Fixed to show scheduled time instead of 0-0 scores"
    }
)

Write-Host "Files to upload:" -ForegroundColor Yellow
foreach ($file in $files) {
    Write-Host "  - $($file.Local)" -ForegroundColor White
    Write-Host "    -> $($file.Description)" -ForegroundColor Gray
}
Write-Host ""

$proceed = Read-Host "Proceed with upload? (yes/no)"
if ($proceed -ne "yes") {
    Write-Host "Upload cancelled" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Opening PythonAnywhere Files page..." -ForegroundColor Cyan
Start-Process "https://www.pythonanywhere.com/user/ABKBet/files/home/ABKBet"

Write-Host ""
Write-Host "=== Upload Instructions ===" -ForegroundColor Yellow
Write-Host "1. Navigate to the /home/ABKBet directory" -ForegroundColor White
Write-Host "2. Upload the following files:" -ForegroundColor White
Write-Host ""

foreach ($file in $files) {
    if (Test-Path $file.Local) {
        Write-Host "   Upload: $($file.Local)" -ForegroundColor Green
        Write-Host "   To: /home/$($file.Remote)" -ForegroundColor Cyan
        Write-Host "   Note: $($file.Description)" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "   ERROR: File not found: $($file.Local)" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "3. After uploading, reload the web app:" -ForegroundColor White
Write-Host "   https://www.pythonanywhere.com/user/ABKBet/webapps/#tab_id_abkbet_pythonanywhere_com" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== What's Fixed ===" -ForegroundColor Yellow
Write-Host "✓ Scheduled games now show time instead of 0-0 scores" -ForegroundColor Green
Write-Host "✓ Betting buttons render as clickable buttons, not text" -ForegroundColor Green
Write-Host "✓ Admin panel shows correct team/game counts" -ForegroundColor Green
Write-Host "✓ Games only show scores when in_progress or finished" -ForegroundColor Green
Write-Host ""

Write-Host "Press any key to open Web App page..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "https://www.pythonanywhere.com/user/ABKBet/webapps/#tab_id_abkbet_pythonanywhere_com"

Write-Host ""
Write-Host "Deployment script complete!" -ForegroundColor Green
Write-Host "Remember to reload the web app after uploading files!" -ForegroundColor Yellow
