import sys
import os
# Ensure project root is on sys.path when running this script from the scripts/ folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import create_app
from app.models import db
import sqlite3

app = create_app()
print("DB URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))
with app.app_context():
    print('Model tables before create_all():', list(db.metadata.tables.keys()))
    db.create_all()
    print("db.create_all() done")
    print('Model tables after create_all():', list(db.metadata.tables.keys()))

# Inspect the actual SQLAlchemy engine URL and attempt to open that file
try:
    engine_url = str(db.engine.url)
    print('Engine URL:', engine_url)
    if engine_url.startswith('sqlite:///'):
        # path after sqlite:///
        db_path = engine_url.replace('sqlite:///', '')
        db_path = os.path.abspath(db_path)
        print('Resolved DB path:', db_path, 'exists?', os.path.exists(db_path))
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            print("Tables in resolved DB:", cur.fetchall())
            conn.close()
except Exception as e:
    print('Error while inspecting engine URL:', e)

# Also check instance path
inst_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'betting.db'))
print('Instance DB path:', inst_path, 'exists?', os.path.exists(inst_path))
if os.path.exists(inst_path):
    conn = sqlite3.connect(inst_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('Tables in instance DB:', cur.fetchall())
    conn.close()
