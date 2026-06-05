from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserProfile, ResumeAnalysis
from schemas import ResumeAnalyzeRequest
from auth import get_current_user
from core.infera_engine import analyze_resume
import json
import io

router = APIRouter(prefix="/resume", tags=["resume"])

def extract_text_from_file(file: UploadFile) -> str:
    content = file.file.read()
    filename = file.filename.lower()
    text = ""
    if filename.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
            text = ""
    elif filename.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            text = ""
    else:
        # Fallback to plain text
        try:
            text = content.decode("utf-8")
        except:
            text = ""
    file.file.seek(0)
    return text

@router.post("/analyze_file")
def analyze_resume_file_route(
    file: UploadFile = File(...),
    company: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    resume_text = extract_text_from_file(file)
    if not resume_text.strip():
        return {"error": "Could not extract text from file or file is empty."}
        
    analysis_data = analyze_resume(resume_text, company, profile)
    
    resume_record = ResumeAnalysis(
        user_id=current_user.id,
        content_text=resume_text,
        ats_score=analysis_data["ats_score"],
        company_optimized_for=company,
        feedback=analysis_data["issues"],
        before_after_examples=analysis_data["before_after"]
    )
    db.add(resume_record)
    db.commit()
    
    return analysis_data


@router.post("/analyze")
def analyze_resume_route(
    req: ResumeAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    analysis_data = analyze_resume(req.resume_text, req.company, profile)
    
    resume_record = ResumeAnalysis(
        user_id=current_user.id,
        content_text=req.resume_text,
        ats_score=analysis_data["ats_score"],
        company_optimized_for=req.company,
        feedback=analysis_data["issues"],
        before_after_examples=analysis_data["before_after"]
    )
    db.add(resume_record)
    db.commit()
    
    return analysis_data

@router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resumes = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == current_user.id).order_by(ResumeAnalysis.analyzed_at.desc()).all()
    return resumes
