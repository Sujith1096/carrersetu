import os
from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AnalysisRecord
from app.schemas import SampleDataResponse
from app.data.sample_data import SAMPLE_JOBS, SAMPLE_RESUME_TEXT
from app.routers.analyze import _process_and_save_analysis

router = APIRouter(prefix="/api/samples", tags=["Samples"])

PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Alex_Rivera_Resume.pdf")

@router.get("/jobs", response_model=List[SampleDataResponse])
def get_sample_jobs():
    """Return realistic industry job postings."""
    return SAMPLE_JOBS

@router.get("/resume")
def get_sample_resume():
    """Return pre-built candidate resume text."""
    return {"resume_text": SAMPLE_RESUME_TEXT, "candidate_name": "Alex Rivera"}

@router.get("/resume-pdf")
def download_sample_pdf():
    """Download sample ATS-optimized PDF resume."""
    if os.path.exists(PDF_PATH):
        return FileResponse(
            PDF_PATH,
            media_type="application/pdf",
            filename="Alex_Rivera_Senior_FullStack_Resume.pdf"
        )
    return {"error": "Sample PDF not found"}

@router.post("/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    """Seed initial realistic analyses so dashboard charts and history are populated immediately."""
    existing_count = db.query(AnalysisRecord).count()
    if existing_count > 0:
        return {"status": "skipped", "message": f"Database already has {existing_count} records."}
        
    created = []
    # Seed Job 1: Senior Full Stack Engineer
    job1 = SAMPLE_JOBS[0]
    rec1 = _process_and_save_analysis(
        resume_text=SAMPLE_RESUME_TEXT,
        jd_text=job1["description"],
        file_name="Alex_Rivera_Resume.pdf",
        job_title=job1["title"],
        job_company=job1["company"],
        db=db
    )
    created.append(rec1.id)
    
    # Seed Job 2: AI / ML Engineer (with slightly lower match to show variance)
    job2 = SAMPLE_JOBS[1]
    rec2 = _process_and_save_analysis(
        resume_text=SAMPLE_RESUME_TEXT,
        jd_text=job2["description"],
        file_name="Alex_Rivera_Resume.pdf",
        job_title=job2["title"],
        job_company=job2["company"],
        db=db
    )
    created.append(rec2.id)

    return {"status": "success", "message": f"Seeded {len(created)} demonstration records.", "ids": created}
