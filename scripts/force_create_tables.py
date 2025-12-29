import sys
import os
# Ensure project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import db
from sqlalchemy import create_engine
import sqlite3

project_db = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'betting.db'))
instance_db = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'betting.db'))

print('Project DB path:', project_db)
print('Instance DB path:', instance_db)

# Import models to ensure metadata is populated
print('Tables in metadata:', list(db.metadata.tables.keys()))

for path in [project_db, instance_db]:
    dirp = os.path.dirname(path)
    os.makedirs(dirp, exist_ok=True)
    engine_url = f"sqlite:///{path}"
    print('\nCreating tables at', engine_url)
    engine = create_engine(engine_url)
    db.metadata.create_all(bind=engine)
    # Inspect created tables via sqlite3
    if os.path.exists(path):
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print('Tables now in', path, ':', cur.fetchall())
        conn.close()
    else:
        print('File not created:', path)

print('\nDone')
