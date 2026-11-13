import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisRecord, User
from app.schemas import HistoryItem, AnalysisResponse, ScoreBreakdown, RecommendationItem
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["History & User Isolation"])

@router.get("", response_model=List[HistoryItem])
def get_history_list(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve resume analysis records belonging EXCLUSIVELY to the authenticated user.
    Strictly isolated: users never see other candidates' reports.
    """
    records = (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.user_id == user.id)
        .order_by(AnalysisRecord.created_at.desc())
        .all()
    )
    results = []
    for r in records:
        try:
            match_skills = json.loads(r.matching_skills or "[]")
            miss_skills = json.loads(r.missing_skills or "[]")
        except Exception:
            match_skills, miss_skills = [], []
            
        results.append(HistoryItem(
            id=r.id,
            created_at=r.created_at.strftime("%b %d, %Y %I:%M %p") if r.created_at else "",
            candidate_name=r.candidate_name or "Candidate",
            candidate_email=r.candidate_email or "",
            job_title=r.job_title or "Target Role",
            job_company=r.job_company or "Company",
            file_name=r.file_name or "resume.pdf",
            overall_score=r.overall_score or 0.0,
            match_rating=r.match_rating or "Needs Optimization",
            matching_skills_count=len(match_skills),
            missing_skills_count=len(miss_skills)
        ))
    return results

@router.get("/{record_id}", response_model=AnalysisResponse)
def get_history_detail(
    record_id: int, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve complete analysis details for a specific record.
    Enforces authorization: returns 403 Forbidden if the record belongs to another user.
    """
    r = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report with ID #{record_id} was not found."
        )
    
    # Strict Authorization check
    if r.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. You do not have authorization to view another user's resume report."
        )
    
    # Parse stored JSON structures
    try:
        extracted = json.loads(r.extracted_skills or "[]")
        matching = json.loads(r.matching_skills or "[]")
        missing = json.loads(r.missing_skills or "[]")
        additional = json.loads(r.additional_skills or "[]")
        sections = json.loads(r.parsed_sections or "{}")
        recs_data = json.loads(r.recommendations or "[]")
        breakdown_data = json.loads(r.score_breakdown or "{}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Corrupted record data: {str(e)}"
        )
        
    recommendations = [RecommendationItem(**item) for item in recs_data]
    score_breakdown = ScoreBreakdown(**breakdown_data)
    
    return AnalysisResponse(
        id=r.id,
        created_at=r.created_at.strftime("%b %d, %Y %I:%M %p") if r.created_at else "",
        candidate_name=r.candidate_name or "Candidate",
        candidate_email=r.candidate_email or "",
        candidate_phone=r.candidate_phone or "",
        candidate_links={},
        file_name=r.file_name or "resume.pdf",
        job_title=r.job_title or "Target Role",
        job_company=r.job_company or "Company",
        overall_score=r.overall_score or 0.0,
        match_rating=r.match_rating or "Needs Optimization",
        score_breakdown=score_breakdown,
        extracted_skills=extracted,
        matching_skills=matching,
        missing_skills=missing,
        additional_skills=additional,
        parsed_sections=sections,
        recommendations=recommendations,
        word_count_resume=len((r.raw_resume_text or "").split()),
        word_count_jd=len((r.raw_job_description or "").split()),
        quantified_metrics_count=0,
        action_verbs_found=[],
        raw_resume_text=r.raw_resume_text,
        raw_job_description=r.raw_job_description
    )

@router.delete("/{record_id}")
def delete_history_record(
    record_id: int, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific resume report.
    Enforces authorization: returns 403 Forbidden if attempting to delete another user's record.
    """
    r = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record #{record_id} not found."
        )
    
    if r.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. You do not have permission to delete another user's report."
        )

    db.delete(r)
    db.commit()
    return {"status": "success", "message": f"Report #{record_id} deleted successfully."}

@router.delete("")
def clear_user_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear all history records belonging to the current user.
    Never affects other users' reports.
    """
    deleted_count = (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.user_id == user.id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {
        "status": "success", 
        "deleted_count": deleted_count, 
        "message": f"Successfully cleared {deleted_count} reports from your private history."
    }
