# PythonAnywhere Quick Start Commands

# 1. Create virtual environment
python3.10 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install packages
pip install -r requirements_pythonanywhere.txt

# 4. Initialize database
python init_db.py

# 5. Populate API matches (optional)
python scripts/populate_api_matches.py

# 6. Test the app locally (optional)
python run.py

# Useful commands:

# Check installed packages
pip list

# Update a package
pip install --upgrade package_name

# Check Python version
python --version

# View error logs (replace YOUR_USERNAME)
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log

# View server logs
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.server.log
