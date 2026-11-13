import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import JobListing, CompanyProfile
from app.schemas import (
    JobItem,
    JobListResponse,
    CompanyItem,
    CompanyListResponse,
    CompanyDetailResponse,
    JobFilterOptionsResponse,
    SyncJobsResponse
)
from app.services.job_aggregator import job_aggregator

router = APIRouter(prefix="/api", tags=["Global Jobs & Companies Explorer"])

def _format_job_item(j: JobListing) -> JobItem:
    try:
        skills_list = json.loads(j.skills) if j.skills else []
    except Exception:
        skills_list = []
        
    return JobItem(
        id=j.id,
        title=j.title,
        company=j.company,
        company_logo=j.company_logo or "",
        company_id=j.company_id or "",
        location=j.location or "Remote",
        city=j.city or "",
        country=j.country or "Global",
        work_mode=j.work_mode or "Remote",
        role_category=j.role_category or "Software Engineering",
        experience_level=j.experience_level or "Mid-level",
        employment_type=j.employment_type or "Full-time",
        salary_min=j.salary_min,
        salary_max=j.salary_max,
        salary_currency=j.salary_currency or "USD",
        salary_text=j.salary_text or "",
        skills=skills_list,
        description=j.description or "",
        url=j.url or "",
        source=j.source or "Verified Portal",
        posted_date=j.posted_date.strftime("%Y-%m-%d") if j.posted_date else "",
        is_active=j.is_active
    )

def _format_company_item(c: CompanyProfile) -> CompanyItem:
    try:
        locations_list = json.loads(c.locations) if c.locations else []
    except Exception:
        locations_list = []

    return CompanyItem(
        id=c.id,
        name=c.name,
        logo=c.logo or "",
        industry=c.industry or "Technology",
        headquarters=c.headquarters or "",
        locations=locations_list,
        website=c.website or "",
        career_page=c.career_page or "",
        description=c.description or "",
        size=c.size or "10,000+ employees",
        founded_year=c.founded_year,
        openings_count=c.openings_count or 0,
        is_featured=c.is_featured or False
    )

# =========================================================================
# JOBS ENDPOINTS
# =========================================================================

@router.get("/jobs", response_model=JobListResponse)
def get_jobs(
    search: Optional[str] = Query(None, description="Keywords in title, company, skills, description"),
    role: Optional[str] = Query(None, description="Role category (Software Engineer, AI/ML, Frontend, etc.)"),
    company: Optional[str] = Query(None, description="Company name or ID"),
    location: Optional[str] = Query(None, description="City or Region"),
    country: Optional[str] = Query(None, description="Country filter (e.g. India, USA, Global)"),
    work_mode: Optional[str] = Query(None, description="Work mode (Remote, Hybrid, On-site)"),
    experience_level: Optional[str] = Query(None, description="Experience level (Internship, Fresher, Senior, etc.)"),
    skills: Optional[str] = Query(None, description="Comma-separated required skills"),
    job_type: Optional[str] = Query(None, description="Employment type (Full-time, Internship, Contract)"),
    salary_min: Optional[float] = Query(None, description="Minimum salary filter"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    sort_by: str = Query("recent", description="'recent' or 'salary'"),
    db: Session = Depends(get_db)
):
    """
    Search and filter global active job postings with pagination.
    """
    items, total, total_pages = job_aggregator.search_jobs(
        db=db,
        search=search,
        role=role,
        company=company,
        location=location,
        country=country,
        work_mode=work_mode,
        experience_level=experience_level,
        skills=skills,
        job_type=job_type,
        salary_min=salary_min,
        page=page,
        limit=limit,
        sort_by=sort_by
    )

    formatted_jobs = [_format_job_item(j) for j in items]

    return JobListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        jobs=formatted_jobs
    )

@router.get("/jobs/{job_id}", response_model=JobItem)
def get_job_detail(job_id: str, db: Session = Depends(get_db)):
    """Fetch complete details for a single job posting."""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job posting with ID '{job_id}' not found."
        )
    return _format_job_item(job)

@router.post("/jobs/sync", response_model=SyncJobsResponse)
def sync_live_jobs(db: Session = Depends(get_db)):
    """
    Triggers live synchronization from external feeds (Remotive, Arbeitnow, Greenhouse).
    Deduplicates and registers active postings in SQLite.
    """
    job_aggregator.ensure_seed_data(db)
    result = job_aggregator.sync_live_jobs(db)
    return SyncJobsResponse(
        status=result["status"],
        message=result["message"],
        fetched=result["fetched"],
        added=result["added"],
        total_active_jobs=result["total_active_jobs"]
    )

@router.get("/jobs/filters/options", response_model=JobFilterOptionsResponse)
def get_filter_options(db: Session = Depends(get_db)):
    """Return distinct filter choices for UI dropdowns."""
    opts = job_aggregator.get_filter_options(db)
    return JobFilterOptionsResponse(
        roles=opts["roles"],
        companies=opts["companies"],
        locations=opts["locations"],
        experience_levels=opts["experience_levels"],
        work_modes=opts["work_modes"],
        employment_types=opts["employment_types"],
        popular_skills=opts["popular_skills"]
    )

# =========================================================================
# COMPANIES ENDPOINTS
# =========================================================================

@router.get("/companies", response_model=CompanyListResponse)
def get_companies(
    search: Optional[str] = Query(None, description="Company name or keyword"),
    industry: Optional[str] = Query(None, description="Industry sector"),
    page: int = Query(1, ge=1),
    limit: int = Query(16, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Search and list enterprise companies hiring across India and globally.
    """
    query = db.query(CompanyProfile)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                CompanyProfile.name.ilike(term),
                CompanyProfile.industry.ilike(term),
                CompanyProfile.headquarters.ilike(term),
                CompanyProfile.description.ilike(term)
            )
        )

    if industry and industry.strip() and industry.lower() != "all":
        query = query.filter(CompanyProfile.industry.ilike(f"%{industry.strip()}%"))

    total = query.count()
    total_pages = max(1, (total + limit - 1) // limit)
    offset = (page - 1) * limit
    
    # Sort by openings count descending, then name
    companies = query.order_by(CompanyProfile.openings_count.desc(), CompanyProfile.name.asc()).offset(offset).limit(limit).all()

    return CompanyListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        companies=[_format_company_item(c) for c in companies]
    )

@router.get("/companies/{company_id}", response_model=CompanyDetailResponse)
def get_company_detail(company_id: str, db: Session = Depends(get_db)):
    """Fetch company profile and all its active job listings."""
    job_aggregator.ensure_seed_data(db)

    company = db.query(CompanyProfile).filter(CompanyProfile.id == company_id).first()
    if not company:
        # Fallback search by slug or name
        company = db.query(CompanyProfile).filter(CompanyProfile.name.ilike(f"%{company_id}%")).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found."
        )

    jobs = db.query(JobListing).filter(
        JobListing.is_active == True,
        or_(
            JobListing.company_id == company.id,
            JobListing.company.ilike(f"%{company.name}%")
        )
    ).order_by(JobListing.posted_date.desc()).all()

    return CompanyDetailResponse(
        company=_format_company_item(company),
        jobs=[_format_job_item(j) for j in jobs]
    )
