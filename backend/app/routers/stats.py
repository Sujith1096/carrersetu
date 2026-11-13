import json
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisRecord
from app.schemas import StatsResponse, HistoryItem

router = APIRouter(prefix="/api/stats", tags=["Statistics"])

@router.get("", response_model=StatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Compute aggregate dashboard metrics, skill frequencies, and score distributions."""
    records = db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).all()
    
    if not records:
        return StatsResponse(
            total_analyses=0,
            average_score=0.0,
            highest_score=0.0,
            lowest_score=0.0,
            score_distribution={
                "< 50": 0,
                "50-69": 0,
                "70-84": 0,
                "85-100": 0
            },
            top_in_demand_skills=[],
            top_missing_skills=[],
            recent_history=[]
        )
        
    total_count = len(records)
    scores = [r.overall_score for r in records if r.overall_score is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    highest = max(scores) if scores else 0.0
    lowest = min(scores) if scores else 0.0
    
    # Distribution buckets
    distribution = {
        "< 50": 0,
        "50-69": 0,
        "70-84": 0,
        "85-100": 0
    }
    for s in scores:
        if s < 50:
            distribution["< 50"] += 1
        elif s < 70:
            distribution["50-69"] += 1
        elif s < 85:
            distribution["70-84"] += 1
        else:
            distribution["85-100"] += 1

    # Skill counters
    matching_counter = Counter()
    missing_counter = Counter()
    
    for r in records:
        try:
            m_skills = json.loads(r.matching_skills or "[]")
            for sk in m_skills:
                matching_counter[sk] += 1
        except Exception:
            pass
            
        try:
            miss_skills = json.loads(r.missing_skills or "[]")
            for sk in miss_skills:
                missing_counter[sk] += 1
        except Exception:
            pass
            
    top_in_demand = [
        {"skill": skill, "count": count, "percentage": round((count / total_count) * 100, 1)}
        for skill, count in matching_counter.most_common(8)
    ]
    
    top_missing = [
        {"skill": skill, "count": count, "percentage": round((count / total_count) * 100, 1)}
        for skill, count in missing_counter.most_common(8)
    ]

    recent_history = []
    for r in records[:5]:
        try:
            m_skills = json.loads(r.matching_skills or "[]")
            miss_skills = json.loads(r.missing_skills or "[]")
        except Exception:
            m_skills, miss_skills = [], []
            
        recent_history.append(HistoryItem(
            id=r.id,
            created_at=r.created_at.strftime("%b %d, %Y %I:%M %p") if r.created_at else "",
            candidate_name=r.candidate_name or "Candidate",
            candidate_email=r.candidate_email or "",
            job_title=r.job_title or "Target Role",
            job_company=r.job_company or "Company",
            file_name=r.file_name or "resume.pdf",
            overall_score=r.overall_score or 0.0,
            match_rating=r.match_rating or "Needs Optimization",
            matching_skills_count=len(m_skills),
            missing_skills_count=len(miss_skills)
        ))

    return StatsResponse(
        total_analyses=total_count,
        average_score=avg_score,
        highest_score=highest,
        lowest_score=lowest,
        score_distribution=distribution,
        top_in_demand_skills=top_in_demand,
        top_missing_skills=top_missing,
        recent_history=recent_history
    )
