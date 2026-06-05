from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = "Ishara"
    location: Optional[str] = "Jodhpur"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    location: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatMessageCreate(BaseModel):
    message: str
    session_id: Optional[int] = None

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    session_type: str
    last_message_at: datetime
    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    skills: Optional[Dict[str, int]] = None
    target_companies: Optional[List[str]] = None
    current_sprint_week: Optional[int] = None

# Phase 2 Schemas
class InterviewStartRequest(BaseModel):
    company: str
    round: str

class InterviewAnswerRequest(BaseModel):
    session_id: int
    question_num: int
    answer: str

class QuizStartRequest(BaseModel):
    topic: str

class QuizAnswerRequest(BaseModel):
    session_id: int
    question_num: int
    answer: str

class ResumeAnalyzeRequest(BaseModel):
    resume_text: str
    company: str
