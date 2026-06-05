from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, MockInterview
from schemas import InterviewStartRequest, InterviewAnswerRequest
from auth import get_current_user
from core.infera_engine import start_interview, submit_interview_answer

router = APIRouter(prefix="/interview", tags=["interview"])

@router.post("/start")
def start_interview_route(
    req: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return start_interview(req.company, req.round, current_user.id, db)

@router.post("/answer")
def submit_answer_route(
    req: InterviewAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return submit_interview_answer(req.session_id, req.question_num, req.answer, current_user.id, db)

@router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interviews = db.query(MockInterview).filter(MockInterview.user_id == current_user.id).order_by(MockInterview.started_at.desc()).all()
    return interviews

@router.get("/{session_id}")
def get_interview(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(MockInterview).filter(MockInterview.id == session_id, MockInterview.user_id == current_user.id).first()
    return interview
