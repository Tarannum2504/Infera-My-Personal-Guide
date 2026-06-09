import asyncio
from database import SessionLocal
from models import User, UserProfile, ChatSession
from core.infera_engine import process_message

async def run_suite():
    db = SessionLocal()
    
    print("\n[TEST SETUP] Initializing memory test suite...")
    
    # Ensure test user exists
    user = db.query(User).filter(User.email == "test@memory.com").first()
    if not user:
        user = User(email="test@memory.com", full_name="Memory Tester")
        user.set_password("password")
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id, memory_notes={})
        db.add(profile)
        db.commit()
        db.refresh(profile)
    else:
        profile.memory_notes = {}
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(profile, "memory_notes")
        db.commit()
        db.refresh(profile)

    # Create dummy session
    session = ChatSession(user_id=user.id, title="Test Session")
    db.add(session)
    db.commit()
    db.refresh(session)

    # Test 1
    print("\n--------------------------------------------------")
    print("TEST 1: Dragonfruit Fact")
    print("--------------------------------------------------")
    profile_data = {"memory_notes": profile.memory_notes}
    
    resp = await process_message(
        message="My favourite fruit is dragonfruit.",
        query_type="GENERAL",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    
    # Mock chat_router regex extraction
    import re, json
    memory_match = re.search(r"<MEMORY>(.*?)</MEMORY>", resp, re.IGNORECASE | re.DOTALL)
    if memory_match:
        try:
            facts = json.loads(memory_match.group(1).strip())
            profile.memory_notes.update(facts)
            flag_modified(profile, "memory_notes")
            db.commit()
        except Exception as e:
            print(f"FAILED TO PARSE JSON: {e}")
            
    # Verification
    profile_data = {"memory_notes": profile.memory_notes}
    resp = await process_message(
        message="What is my favourite fruit?",
        query_type="GENERAL",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    print(f"AI: {resp}")
    if "dragonfruit" in resp.lower() and ("source: memory database" in resp.lower() or "memory database" in resp.lower()):
        print("[PASS] Test 1 passed.")
    else:
        print("[FAIL] Test 1 failed.")


    # Test 2
    print("\n--------------------------------------------------")
    print("TEST 2: CGPA Fact")
    print("--------------------------------------------------")
    resp = await process_message(
        message="My CGPA is 9.7.",
        query_type="GENERAL",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    
    memory_match = re.search(r"<MEMORY>(.*?)</MEMORY>", resp, re.IGNORECASE | re.DOTALL)
    if memory_match:
        try:
            facts = json.loads(memory_match.group(1).strip())
            profile.memory_notes.update(facts)
            flag_modified(profile, "memory_notes")
            db.commit()
        except Exception as e:
            pass
            
    profile_data = {"memory_notes": profile.memory_notes}
    resp = await process_message(
        message="What is my CGPA?",
        query_type="GENERAL",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    print(f"AI: {resp}")
    if "9.7" in resp and ("source: memory database" in resp.lower() or "memory database" in resp.lower()):
        print("[PASS] Test 2 passed.")
    else:
        print("[FAIL] Test 2 failed.")


    # Test 3
    print("\n--------------------------------------------------")
    print("TEST 3: Internship Fact")
    print("--------------------------------------------------")
    resp = await process_message(
        message="I am interning at SIN Education as Data Studio Intern.",
        query_type="GENERAL",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    
    memory_match = re.search(r"<MEMORY>(.*?)</MEMORY>", resp, re.IGNORECASE | re.DOTALL)
    if memory_match:
        try:
            facts = json.loads(memory_match.group(1).strip())
            profile.memory_notes.update(facts)
            flag_modified(profile, "memory_notes")
            db.commit()
        except Exception as e:
            pass
            
    profile_data = {"memory_notes": profile.memory_notes}
    resp = await process_message(
        message="Where am I interning?",
        query_type="GENERAL",
        user_profile=profile_data,
        user_id=user.id,
        db=db,
        history=[]
    )
    print(f"AI: {resp}")
    if "sin education" in resp.lower() and "data studio intern" in resp.lower():
        print("[PASS] Test 3 passed.")
    else:
        print("[FAIL] Test 3 failed.")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(run_suite())
