from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserProfile
from schemas import ProfileUpdate
from auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return profile

@router.put("/")
def update_profile(profile_data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile_data.skills:
        profile.skills = profile_data.skills
    if profile_data.target_companies:
        profile.target_companies = profile_data.target_companies
    if profile_data.current_sprint_week:
        profile.current_sprint_week = profile_data.current_sprint_week
        
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/dashboard-data")
def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from sqlalchemy import text as sql_text
    from datetime import datetime, timedelta

    # Real mock interview scores
    interviews = db.execute(
        sql_text(
            "SELECT overall_score, completed_at, company "
            "FROM mock_interviews "
            "WHERE user_id = :uid AND status = 'completed' "
            "ORDER BY completed_at ASC LIMIT 10"
        ),
        {"uid": current_user.id}
    ).fetchall()

    mock_trend = []
    if interviews:
        for i, row in enumerate(interviews, 1):
            mock_trend.append({
                "label": f"Mock {i}",
                "score": float(row[0]) * 10 if row[0] else 0,
                "company": row[2] or "Celebal"
            })

    # Real sprint progress from user profile
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    skills = {}
    sprint_week = 1
    projects = []
    if profile:
        skills = profile.skills or {}
        sprint_week = profile.current_sprint_week or 1
        projects = profile.projects or []

    # Calculate sprint completion based on actual skill improvements
    base_skills = {
        "SQL": 80, "Python": 65, "Power BI": 20,
        "Statistics": 40, "Azure": 15, "Databricks": 5
    }
    current_avg = sum(skills.get(k, base_skills[k])
                     for k in base_skills) / len(base_skills)
    target_avg = 80
    completion_pct = min(
        99,
        int(((current_avg - 35) / (target_avg - 35)) * 100)
    )
    days_remaining = max(0, 84 - (sprint_week - 1) * 7)

    # Default projects if none set
    if not projects:
        projects = [
            {"name": "AskQL", "status": "built"},
            {"name": "SQL Analytics", "status": "built"},
            {"name": "Power BI Dashboard", "status": "not_started"},
            {"name": "HR Analytics Dashboard", "status": "not_started"},
            {"name": "Customer Churn Analysis", "status": "not_started"}
        ]

    # Real quiz average
    quiz_avg_row = db.execute(
        sql_text(
            "SELECT AVG(overall_score) FROM quiz_sessions "
            "WHERE user_id = :uid AND status = 'completed'"
        ),
        {"uid": current_user.id}
    ).fetchone()
    quiz_avg = float(quiz_avg_row[0]) if quiz_avg_row and quiz_avg_row[0] else None

    # Calculate dynamic readiness
    celebal_weights = {"SQL": 0.3, "Power BI": 0.3, "Python": 0.2, "Communication": 0.2}
    tcs_weights = {"DBMS": 0.3, "OOP": 0.3, "DSA": 0.2, "Python": 0.2}
    optum_weights = {"Python": 0.3, "SQL": 0.3, "Statistics": 0.2, "Azure": 0.2}

    def calc_readiness(weights, user_skills):
        score = 0
        for skill, weight in weights.items():
            skill_val = user_skills.get(skill, base_skills.get(skill, 30))
            score += skill_val * weight
        return int(score)

    celebal_readiness = calc_readiness(celebal_weights, skills)
    tcs_readiness = calc_readiness(tcs_weights, skills)
    optum_readiness = calc_readiness(optum_weights, skills)
    overall_readiness = int((celebal_readiness + tcs_readiness + optum_readiness) / 3)

    readiness = {
        "overall": overall_readiness,
        "celebal": celebal_readiness,
        "tcs": tcs_readiness,
        "optum": optum_readiness
    }

    return {
        "skills": skills,
        "mock_trend": mock_trend,
        "sprint": {
            "week": sprint_week,
            "total_weeks": 12,
            "completion_pct": completion_pct,
            "days_remaining": days_remaining
        },
        "projects": projects,
        "quiz_avg": quiz_avg,
        "has_mock_data": len(mock_trend) > 0,
        "has_quiz_data": quiz_avg is not None,
        "readiness": readiness
    }

from typing import List
from pydantic import BaseModel
class ProjectItem(BaseModel):
    name: str
    status: str

@router.put("/projects")
def update_projects(
    projects: List[ProjectItem],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        profile.projects = [{"name": p.name, "status": p.status} for p in projects]
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(profile, "projects")
        db.commit()
    return {"message": "Projects updated"}
