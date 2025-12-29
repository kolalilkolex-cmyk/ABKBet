#!/bin/bash
# Quick Start Script for ABKBet

echo "==================================="
echo "ABKBet - Bitcoin Betting Platform"
echo "==================================="
echo ""

# Check Python version
python --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Python is not installed"
    exit 1
fi

echo "✓ Python is installed"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created - Please edit with your settings"
fi

# Initialize database
echo "Initializing database..."
python manage_db.py init

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source venv/bin/activate (Linux/Mac)"
echo "                                   venv\Scripts\activate (Windows)"
echo "  2. Run the application: python run.py"
echo ""
echo "Server will be available at: http://localhost:5000"
echo ""
