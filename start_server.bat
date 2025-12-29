@echo off
echo =========================================
echo Starting ABKBet Flask Server
echo =========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv_3.12\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Set environment variables
set PYTHONPATH=%CD%
set FLASK_ENV=development
set FLASK_DEBUG=1

echo Starting Flask server...
echo.
echo Server will be accessible at:
echo   - http://127.0.0.1:5000 (your computer)
echo   - http://10.40.140.99:5000 (phone via hotspot)
echo.
echo Press Ctrl+C to stop the server
echo =========================================
echo.

REM Start the server
venv_3.12\Scripts\python.exe run.py

pause
