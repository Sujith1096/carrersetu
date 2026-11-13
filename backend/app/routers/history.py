import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisRecord
from app.schemas import HistoryItem, AnalysisResponse, ScoreBreakdown, RecommendationItem

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("", response_model=List[HistoryItem])
def get_history_list(db: Session = Depends(get_db)):
    """Retrieve all past resume analysis records."""
    records = db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).all()
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
def get_history_detail(record_id: int, db: Session = Depends(get_db)):
    """Retrieve complete analysis details for a specific record."""
    r = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report with ID {record_id} not found."
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
            detail=f"Error parsing stored record JSON: {str(e)}"
        )

    recommendations = [RecommendationItem(**item) for item in recs_data]
    
    score_breakdown = ScoreBreakdown(
        skills_score=r.skills_score or 0.0,
        similarity_score=r.similarity_score or 0.0,
        section_score=r.section_score or 0.0,
        metrics_score=r.metrics_score or 0.0,
        overall_score=r.overall_score or 0.0,
        match_rating=r.match_rating or "Needs Optimization",
        explanation=breakdown_data.get("explanation", {})
    )

    word_count_resume = len((r.raw_resume_text or "").split())
    word_count_jd = len((r.raw_job_description or "").split())

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
        word_count_resume=word_count_resume,
        word_count_jd=word_count_jd,
        quantified_metrics_count=int((r.metrics_score or 0) / 8.5),
        action_verbs_found=[],
        raw_resume_text=r.raw_resume_text,
        raw_job_description=r.raw_job_description
    )

@router.delete("/{record_id}")
def delete_history_record(record_id: int, db: Session = Depends(get_db)):
    """Delete an analysis report by ID."""
    r = db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record {record_id} not found."
        )
    db.delete(r)
    db.commit()
    return {"status": "success", "message": f"Report #{record_id} successfully deleted."}

@router.delete("")
def clear_all_history(db: Session = Depends(get_db)):
    """Clear all past analysis reports."""
    count = db.query(AnalysisRecord).delete()
    db.commit()
    return {"status": "success", "message": f"Cleared {count} historical reports."}
