from app import app, db, session

with app.app_context():
    db.create_all()
