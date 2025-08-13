import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.Database.database import SessionLocal, User
from backend.Database.auth import get_password_hash

# Create a new session
db = SessionLocal()

# Create a new user
new_user = User(
    name="New User Name",
    email="newuser@example.com",
    password_hash=get_password_hash("securepassword123")
)

# Add and commit
db.add(new_user)
db.commit()

# Close the session
db.close()

print("✅ New user added to the database.")