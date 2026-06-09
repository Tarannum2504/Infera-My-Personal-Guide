import os
import asyncio
from dotenv import load_dotenv

# Set to use sqlite locally
os.environ["DATABASE_URL"] = "sqlite:///./infera.db"
load_dotenv()

from database import SessionLocal
from core.infera_engine import process_message
from routers.chat_router import get_current_user # Wait, we can't use FastAPI depends. We'll just fetch a user.
from models import User, UserProfile
import re

async def run_test():
    db = SessionLocal()
    
    # Ensure test user exists
    user = db.query(User).first()
    if not user:
        user = User(email="test@test.com", full_name="Test User")
        user.set_password("password")
        db.add(user)
        db.commit()
        db.refresh(user)

    # Ensure memory_notes exists locally (mock migration if needed)
    from sqlalchemy.sql import text
    try:
        db.execute(text("SELECT memory_notes FROM user_profiles LIMIT 1"))
    except Exception:
        db.rollback()
        # DB doesn't have it locally, alter table
        db.execute(text("ALTER TABLE user_profiles ADD COLUMN memory_notes JSON DEFAULT '[]'"))
        db.commit()
        
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id, memory_notes=[])
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    profile_data = {
        "skills": profile.skills or {},
        "target_companies": profile.target_companies or [],
        "current_sprint_week": profile.current_sprint_week or 1,
        "placement_readiness": profile.placement_readiness or 70,
        "memory_notes": profile.memory_notes or []
    }
    
    print("--------------------------------------------------")
    print("TEST 1: User states a fact")
    print("--------------------------------------------------")
    msg1 = "My CGPA is 9.7"
    print(f"User: {msg1}")
    
    # We must manually inject the router logic since we are bypassing HTTP
    response_text = await process_message(
        message=msg1,
        query_type="general",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    
    # Replicate router memory extraction logic
    print(f"[MEMORY LOG] Checking AI response for <MEMORY> tag...")
    memory_match = re.search(r"<MEMORY>(.*?)</MEMORY>", response_text, re.IGNORECASE | re.DOTALL)
    if memory_match:
        new_fact = memory_match.group(1).strip()
        print(f"[MEMORY LOG] SUCCESS - Memory extracted: '{new_fact}'")
        response_text = re.sub(r"<MEMORY>.*?</MEMORY>", "", response_text, flags=re.IGNORECASE | re.DOTALL).strip()
        
        current_notes = profile.memory_notes or []
        print(f"[MEMORY LOG] Current DB memory notes before save: {current_notes}")
        if new_fact not in current_notes:
            current_notes.append(new_fact)
            profile.memory_notes = list(current_notes)
            db.commit()
            print(f"[MEMORY LOG] SUCCESS - Memory saved to database. Updated notes: {profile.memory_notes}")
    
    print(f"AI: {response_text}")
    
    print("\n--------------------------------------------------")
    print("TEST 2: User asks about the fact in a new chat")
    print("--------------------------------------------------")
    
    # Refresh profile data for new chat
    db.refresh(profile)
    profile_data["memory_notes"] = profile.memory_notes or []
    
    msg2 = "What is my CGPA?"
    print(f"User: {msg2}")
    response_text2 = await process_message(
        message=msg2,
        query_type="general",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    
    # Clean output just in case
    response_text2 = re.sub(r"<MEMORY>.*?</MEMORY>", "", response_text2, flags=re.IGNORECASE | re.DOTALL).strip()
    
    print(f"AI: {response_text2}")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(run_test())
