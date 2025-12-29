@echo off
echo ========================================
echo Starting ABKBet Application
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python environment...
if not exist "venv_3.12\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

echo Checking database...
if not exist "instance\betting.db" (
    echo WARNING: Database not found. It will be created on first run.
)

echo.
echo Starting Flask application...
echo Access from computer: http://127.0.0.1:5000
echo Access from phone: http://10.40.140.99:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

venv_3.12\Scripts\python.exe run.py

pause
