from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, QuizSession
from schemas import QuizStartRequest, QuizAnswerRequest
from auth import get_current_user
from core.infera_engine import start_quiz, submit_quiz_answer

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/start")
def start_quiz_route(
    req: QuizStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return start_quiz(req.topic, current_user.id, db)

@router.post("/answer")
async def submit_answer_route(
    req: QuizAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await submit_quiz_answer(req.session_id, req.question_num, req.answer, current_user.id, db)

@router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quizzes = db.query(QuizSession).filter(QuizSession.user_id == current_user.id).order_by(QuizSession.created_at.desc()).all()
    return quizzes
