from app import app
from extensions import db
from models import User

with app.app_context():
    users = User.query.all()
    if users:
        print(f"Found {len(users)} user(s):")
        for user in users:
            print(f"- Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Password Hash: {user.password_hash[:50]}...")  # First 50 chars
            print()
    else:
        print("No users found in database.")