import sys
sys.path.insert(0, r"C:\Users\HP\Documents\ABKBet")
from run import create_app

app = create_app()
with app.app_context():
    from app.models import db
    db.create_all()
    print(" Tables created successfully")
