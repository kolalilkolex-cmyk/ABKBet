# WSGI Configuration for PythonAnywhere
# This file should be copied to your PythonAnywhere WSGI configuration

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/Lilkolex/ABKBet'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Set default environment variables if not already set
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'change-this-to-a-random-secret-key'
if not os.environ.get('FOOTBALL_API_KEY'):
    os.environ['FOOTBALL_API_KEY'] = '56c4696d55ef31100dc857478bbf61b8'
if not os.environ.get('FOOTBALL_API_ENABLED'):
    os.environ['FOOTBALL_API_ENABLED'] = 'true'

# Import Flask app
from run import flask_app as application

# For PythonAnywhere, we need to export 'application'
# PythonAnywhere looks for a variable named 'application' in the WSGI file
