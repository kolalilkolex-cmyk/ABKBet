# PowerShell script to compress all recently changed ABKBet files for upload
Compress-Archive -Path `
  templates\index.html,`
  templates\admin.html,`
  static\abkbet-client.js,`
  app\routes\admin_routes.py,`
  app\routes\bet_routes.py,`
  app\models\__init__.py,`
  app\routes\auth_routes.py
  -DestinationPath abkbet_update.zip
Write-Host "Created abkbet_update.zip with all updated files."