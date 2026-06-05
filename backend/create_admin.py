import asyncio
import sys
import os

# Add the backend directory to path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import User
from auth import get_password_hash

async def create_admin():
    db = SessionLocal()
    email = "ishara@infera.app"
    password = "InferaAI2026!"
    
    # Check if user already exists
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"User {email} already exists.")
        db.close()
        return

    # Create new admin user
    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        password_hash=hashed_password,
        full_name="Ishara"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"Admin account created successfully: {email}")
    db.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
