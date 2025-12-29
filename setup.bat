@echo off
REM Quick Start Script for ABKBet (Windows PowerShell version)

echo ===================================
echo ABKBet - Bitcoin Betting Platform
echo ===================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    exit /b 1
)

echo [OK] Python is installed

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [OK] Virtual environment activated

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [OK] Dependencies installed

REM Create .env file
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo [OK] .env file created - Please edit with your settings
)

REM Initialize database
echo Initializing database...
python manage_db.py init

echo.
echo ===================================
echo Setup Complete!
echo ===================================
echo.
echo To start the server:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run the application: python run.py
echo.
echo Server will be available at: http://localhost:5000
echo.
