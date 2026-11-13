import json
from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisRecord
from app.schemas import AnalysisResponse, AnalyzeTextRequest, ScoreBreakdown, RecommendationItem
from app.services.pdf_parser import extract_text_from_pdf_bytes, parse_contact_info, segment_resume_sections
from app.services.ml_engine import calculate_ats_score
from app.services.recommendations import generate_recommendations

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_TEXT_LENGTH = 100_000         # 100,000 characters

def _process_and_save_analysis(
    resume_text: str,
    jd_text: str,
    file_name: str,
    job_title: str,
    job_company: str,
    db: Session
) -> AnalysisResponse:
    cleaned_resume = resume_text.strip()
    cleaned_jd = jd_text.strip()

    if not cleaned_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is empty. Please provide resume content to evaluate."
        )
    if len(cleaned_resume) < 30:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume content is too short for a meaningful ATS assessment. Please provide at least 30 characters."
        )
    if not cleaned_jd:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is empty. Please paste the job requirements to compare against."
        )
    if len(cleaned_jd) < 15:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Job description is too brief. Please provide detailed job responsibilities and required skills."
        )

    # Sanitize title & company lengths for database limits
    safe_title = (job_title or "Target Role").strip()[:200]
    safe_company = (job_company or "Company").strip()[:200]
    safe_filename = (file_name or "Resume.pdf").strip()[:200]

    # Contact & links extraction
    candidate_name, email, phone, links = parse_contact_info(cleaned_resume)
    
    # Section segmentation
    sections = segment_resume_sections(cleaned_resume)
    
    # ML & ATS scoring engine
    scoring = calculate_ats_score(cleaned_resume, cleaned_jd, sections)
    
    # Actionable recommendations
    recs = generate_recommendations(scoring, sections, links)
    
    # Score breakdown object
    score_breakdown = ScoreBreakdown(
        skills_score=scoring["skills_score"],
        similarity_score=scoring["similarity_score"],
        section_score=scoring["section_score"],
        metrics_score=scoring["metrics_score"],
        overall_score=scoring["overall_score"],
        match_rating=scoring["match_rating"],
        explanation=scoring["explanation"]
    )
    
    # Store in database
    db_record = AnalysisRecord(
        candidate_name=candidate_name,
        candidate_email=email,
        candidate_phone=phone,
        file_name=safe_filename,
        job_title=safe_title,
        job_company=safe_company,
        overall_score=scoring["overall_score"],
        match_rating=scoring["match_rating"],
        skills_score=scoring["skills_score"],
        similarity_score=scoring["similarity_score"],
        section_score=scoring["section_score"],
        metrics_score=scoring["metrics_score"],
        extracted_skills=json.dumps(scoring["resume_skills"]),
        matching_skills=json.dumps(scoring["matching_skills"]),
        missing_skills=json.dumps(scoring["missing_skills"]),
        additional_skills=json.dumps(scoring["additional_skills"]),
        parsed_sections=json.dumps(sections),
        recommendations=json.dumps([r.model_dump() for r in recs]),
        score_breakdown=json.dumps(score_breakdown.model_dump()),
        raw_resume_text=cleaned_resume[:MAX_TEXT_LENGTH],
        raw_job_description=cleaned_jd[:MAX_TEXT_LENGTH]
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # Word count statistics
    word_count_resume = len(cleaned_resume.split())
    word_count_jd = len(cleaned_jd.split())
    
    return AnalysisResponse(
        id=db_record.id,
        created_at=db_record.created_at.strftime("%b %d, %Y %I:%M %p"),
        candidate_name=candidate_name,
        candidate_email=email,
        candidate_phone=phone,
        candidate_links=links,
        file_name=safe_filename,
        job_title=safe_title,
        job_company=safe_company,
        overall_score=scoring["overall_score"],
        match_rating=scoring["match_rating"],
        score_breakdown=score_breakdown,
        extracted_skills=scoring["resume_skills"],
        matching_skills=scoring["matching_skills"],
        missing_skills=scoring["missing_skills"],
        additional_skills=scoring["additional_skills"],
        parsed_sections=sections,
        recommendations=recs,
        word_count_resume=word_count_resume,
        word_count_jd=word_count_jd,
        quantified_metrics_count=scoring["metrics_count"],
        action_verbs_found=scoring["action_verbs"],
        raw_resume_text=cleaned_resume,
        raw_job_description=cleaned_jd
    )

@router.post("/upload", response_model=AnalysisResponse)
async def analyze_pdf_upload(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: str = Form("Target Role"),
    job_company: str = Form("Company"),
    db: Session = Depends(get_db)
):
    """Upload PDF resume, extract text via PyMuPDF, and run ATS analysis against JD."""
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF documents (.pdf) are supported."
        )

    # Read content with 10MB limit enforcement
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded PDF file exceeds the 10 MB maximum allowed size."
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF file is empty (0 bytes). Please upload a valid document."
        )

    try:
        resume_text = extract_text_from_pdf_bytes(content)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"PDF extraction error: {str(e)}"
        )

    return _process_and_save_analysis(
        resume_text=resume_text,
        jd_text=job_description,
        file_name=file.filename or "Uploaded_Resume.pdf",
        job_title=job_title,
        job_company=job_company,
        db=db
    )

@router.post("/text", response_model=AnalysisResponse)
async def analyze_text(
    payload: AnalyzeTextRequest,
    db: Session = Depends(get_db)
):
    """Analyze directly pasted resume text against job description."""
    return _process_and_save_analysis(
        resume_text=payload.resume_text,
        jd_text=payload.job_description,
        file_name=payload.file_name or "Pasted_Resume.txt",
        job_title=payload.job_title or "Target Role",
        job_company=payload.job_company or "Company",
        db=db
    )
