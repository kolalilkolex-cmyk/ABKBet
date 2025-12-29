# Start-dev: activates venv and runs the Flask app, tails logs
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

# Activate venv (PowerShell execution policy may block Activate.ps1; run this script from an elevated shell if needed)
$venvPython = Join-Path $root 'venv_3.12\Scripts\python.exe'
if (-Not (Test-Path $venvPython)) {
    Write-Error "Python in venv not found at $venvPython"
    exit 1
}

# Ensure logs dir exists
$logs = Join-Path $root 'logs'
if (-Not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

# Start the app in background, redirecting stdout/stderr to logs
Start-Process -FilePath $venvPython -ArgumentList 'run.py' -WorkingDirectory $root -NoNewWindow -PassThru -RedirectStandardOutput "$logs\run_stdout.log" -RedirectStandardError "$logs\run_stderr.log"
Write-Output "Server started; logs -> $logs\run_stdout.log (stdout) and $logs\run_stderr.log (stderr)"

# Tail logs
Write-Output "Tailing logs (press Ctrl+C to stop)"
Get-Content "$logs\run_stdout.log" -Wait -Tail 20
