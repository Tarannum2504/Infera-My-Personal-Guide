from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import traceback
import re

from database import get_db
from models import ChatSession, ChatMessage, UserProfile, User
from auth import get_current_user
from core.infera_engine import process_message
from core.query_classifier import classify

router = APIRouter(prefix="/chat", tags=["chat"])


class MessageRequest(BaseModel):
    message: str
    session_id: Optional[int] = None


class RenameRequest(BaseModel):
    title: str


@router.get("/debug/memory")
def debug_memory(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    stored = {}
    if profile:
        stored = profile.memory_notes or {}
    
    loaded = {}
    injected_count = 0
    if isinstance(stored, dict):
        loaded = stored
        injected_count = len(stored.keys())
    elif isinstance(stored, list):
        import json
        for item in stored:
            try:
                if isinstance(item, str):
                    parsed = json.loads(item)
                    if isinstance(parsed, dict):
                        loaded.update(parsed)
            except Exception:
                pass
        injected_count = len(loaded.keys())

    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "stored_memory": stored,
        "loaded_memory": loaded,
        "injected_memory_count": injected_count
    }

@router.post("/send")
async def send_message(
    message: str = Form(default=""),
    session_id: Optional[int] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from core.file_parser import extract_pdf_text, extract_docx_text
    
    file_context = ""
    file_name = ""

    # Handle file if attached
    if file and file.filename:
        file_name = file.filename
        file_bytes = await file.read()
        ext = file.filename.lower().split(".")[-1]

        if ext == "pdf":
            file_context = extract_pdf_text(file_bytes)
        elif ext in ["txt", "md"]:
            file_context = file_bytes.decode("utf-8", errors="ignore")
        elif ext in ["png", "jpg", "jpeg", "gif", "webp"]:
            file_context = f"[Image uploaded: {file.filename}]"
        elif ext in ["docx"]:
            file_context = extract_docx_text(file_bytes)
        else:
            file_context = f"[File uploaded: {file.filename}]"

    # If message is empty but file was uploaded, create auto message
    if not message.strip() and file_context:
        message = f"I uploaded {file_name}. Please analyze it."
    elif not message.strip():
        message = "Hello"

    # Combine message + file context for processing
    full_context = message
    if file_context:
        full_context = (
            f"{message}\n\n"
            f"[ATTACHED FILE: {file_name}]\n"
            f"{file_context[:3000]}"
        )

    try:
        # Safely parse session_id
        session_id_int = None
        if session_id is not None:
            try:
                session_id_int = int(session_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid session_id format")

        # Get or create session
        if session_id_int:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id_int,
                ChatSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(status_code=404,
                                    detail="Session not found")
        else:
            # Create new session with title from first message
            title = message[:50] if message else "New Chat"
            session = ChatSession(
                user_id=current_user.id,
                title=title,
                session_type="chat"
            )
            db.add(session)
            db.flush()  # get session.id without committing

        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            user_id=current_user.id,
            role="user",
            content=message,
            message_type="text"
        )
        db.add(user_msg)

        # Get user profile for context
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        profile_data = {}
        if profile:
            profile_data = {
                "skills": profile.skills or {},
                "target_companies": profile.target_companies or [],
                "current_sprint_week": profile.current_sprint_week or 1,
                "placement_readiness": profile.placement_readiness or 70,
                "memory_notes": profile.memory_notes or []
            }

        # Generate INFERA response
        query_type = classify(full_context)

        # Fetch recent chat history for context memory
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id,
            ChatMessage.id != user_msg.id  # Exclude current message since it's passed separately
        ).order_by(ChatMessage.created_at.desc()).limit(6).all()
        
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(recent_messages)
        ]

        # Intercept /show-memory
        if full_context.strip() == "/show-memory":
            import json
            current_notes = profile.memory_notes or {}
            
            # Automatic Migration for display
            if isinstance(current_notes, list):
                migrated_notes = {}
                for item in current_notes:
                    try:
                        if isinstance(item, str):
                            parsed = json.loads(item)
                            if isinstance(parsed, dict):
                                migrated_notes.update(parsed)
                    except Exception:
                        pass
                current_notes = migrated_notes
                
            mem_str = "\n".join([f"{k.replace('_', ' ').title()}:\n{v}\n" for k, v in current_notes.items()])
            response_text = f"Current Stored Memory\n\n{mem_str}" if mem_str else "Current Stored Memory\n\nNone"
            
            return JSONResponse({
                "response": response_text,
                "session_id": session.id,
                "session_title": session.title,
                "message_id": 999999
            })

        response_text = await process_message(
            message=full_context,
            query_type=query_type,
            user_profile=profile_data,
            user_id=current_user.id,
            db=db,
            history=history
        )

        # Extract and save new memory notes
        print(f"[MEMORY DEBUG]\nChecking AI response for <MEMORY> tag...")
        memory_match = re.search(r"<MEMORY>(.*?)</MEMORY>", response_text, re.IGNORECASE | re.DOTALL)
        if memory_match:
            raw_json = memory_match.group(1).strip()
            print(f"[MEMORY DEBUG]\nExtracted:\n{raw_json}")
            
            # Remove the tag from the final response
            response_text = re.sub(r"<MEMORY>.*?</MEMORY>", "", response_text, flags=re.IGNORECASE | re.DOTALL).strip()
            
            if profile:
                import json
                current_notes = profile.memory_notes or {}
                
                # Automatic Migration
                if isinstance(current_notes, list):
                    migrated_notes = {}
                    for item in current_notes:
                        try:
                            if isinstance(item, str):
                                parsed = json.loads(item)
                                if isinstance(parsed, dict):
                                    migrated_notes.update(parsed)
                        except Exception:
                            pass
                    current_notes = migrated_notes

                try:
                    # Strip potential markdown formatting from AI output
                    clean_json = raw_json.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    elif clean_json.startswith("```"):
                        clean_json = clean_json[3:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    clean_json = clean_json.strip()

                    new_facts = json.loads(clean_json)
                    if isinstance(new_facts, dict):
                        current_notes.update(new_facts)
                        
                        from sqlalchemy.orm.attributes import flag_modified
                        # Reassign as a completely new dictionary to ensure SQLAlchemy detects the change
                        profile.memory_notes = dict(current_notes)
                        flag_modified(profile, "memory_notes")
                        db.commit()
                        print(f"[MEMORY DEBUG]\nSaving:\n{json.dumps(new_facts, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"[MEMORY DEBUG]\nFailed to parse JSON memory: {raw_json}\nError: {e}")
        else:
            print(f"[MEMORY DEBUG]\nNo <MEMORY> tag found in AI response.")

        # Save INFERA response
        infera_msg = ChatMessage(
            session_id=session.id,
            user_id=current_user.id,
            role="infera",
            content=response_text,
            message_type="text"
        )
        db.add(infera_msg)

        # Update session last_message_at
        from datetime import datetime
        session.last_message_at = datetime.utcnow()

        db.commit()

        return {
            "session_id": session.id,
            "user_message": message,
            "infera_response": response_text,
            "query_type": query_type
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Chat error: {traceback.format_exc()}")
        # Return a helpful fallback instead of crashing
        return {
            "session_id": session_id_int or 0,
            "user_message": message,
            "infera_response": (
                "INFERA encountered an internal error processing "
                "your message. The error has been logged. "
                "Please try again or ask a different question."
            ),
            "query_type": "error",
            "error": str(e)
        }


@router.get("/sessions")
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.last_message_at.desc()).limit(50).all()

    return [
        {
            "id": s.id,
            "title": s.title or "Untitled Chat",
            "session_type": s.session_type or "chat",
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "last_message_at": (s.last_message_at.isoformat()
                                if s.last_message_at else None)
        }
        for s in sessions
    ]


@router.get("/session/{session_id}")
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "message_type": m.message_type,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in messages
    ]


@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Delete all messages in session first
    db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).delete()

    db.delete(session)
    db.commit()

    return {"message": "Chat deleted successfully"}


@router.put("/session/{session_id}/rename")
def rename_session(
    session_id: int,
    request: RenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.title = request.title[:100]
    db.commit()

    return {"message": "Renamed successfully", "title": session.title}
