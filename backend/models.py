import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), default='Ishara')
    location = Column(String(100), default='Jodhpur')
    year_of_study = Column(Integer, default=3)
    branch = Column(String(100), default='CSE AI/ML')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    chat_sessions = relationship("ChatSession", back_populates="user")
    mock_interviews = relationship("MockInterview", back_populates="user")
    quiz_sessions = relationship("QuizSession", back_populates="user")
    resumes = relationship("ResumeAnalysis", back_populates="user")
    skill_progressions = relationship("SkillProgression", back_populates="user")
    decisions = relationship("DecisionLog", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    skills = Column(JSON, default={
        "SQL": 80, "Python": 65, "Power BI": 20,
        "Statistics": 40, "Business Analytics": 35,
        "Azure": 15, "Databricks": 5, "DSA": 30,
        "DBMS": 72, "OOP": 68, "Communication": 55
    })
    target_companies = Column(JSON, default=["Celebal Technologies", "TCS Digital", "Optum"])
    current_sprint_week = Column(Integer, default=1)
    placement_readiness = Column(Integer, default=70)
    projects = Column(JSON, default=[])
    certifications = Column(JSON, default=[])
    memory_notes = Column(JSON, default=[])
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), default='New Chat')
    session_type = Column(String(50), default='chat')
    company_context = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False) # 'user', 'infera'
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default='text')
    metadata_json = Column("metadata", JSON, default={})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
    user = relationship("User")

class MockInterview(Base):
    __tablename__ = "mock_interviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    company = Column(String(100))
    interview_round = Column(String(100))
    questions = Column(JSON, default=[])
    answers = Column(JSON, default=[])
    scores = Column(JSON, default=[])
    overall_score = Column(Numeric(5, 2))
    feedback_summary = Column(Text)
    weak_areas = Column(JSON, default=[])
    status = Column(String(50), default='in_progress')
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="mock_interviews")

class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    topic = Column(String(100))
    company = Column(String(100))
    difficulty = Column(String(50), default='medium')
    questions = Column(JSON, default=[])
    user_answers = Column(JSON, default=[])
    scores = Column(JSON, default=[])
    overall_score = Column(Numeric(5, 2))
    feedback = Column(Text)
    weak_topics = Column(JSON, default=[])
    status = Column(String(50), default='in_progress')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="quiz_sessions")

class ResumeAnalysis(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content_text = Column(Text)
    parsed_data = Column(JSON, default={})
    ats_score = Column(Numeric(5, 2))
    company_optimized_for = Column(String(100))
    feedback = Column(JSON, default={})
    before_after_examples = Column(JSON, default=[])
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="resumes")

class SkillProgression(Base):
    __tablename__ = "skill_progression"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    skill_name = Column(String(100))
    score = Column(Integer)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="skill_progressions")

class DecisionLog(Base):
    __tablename__ = "decisions_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    question = Column(Text)
    recommendation = Column(Text)
    reason = Column(Text)
    opportunity_cost = Column(Text)
    expected_outcome = Column(Text)
    confidence_score = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="decisions")
