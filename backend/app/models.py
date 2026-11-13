from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from app.database import Base

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    candidate_name = Column(String(255), default="Unknown Candidate")
    candidate_email = Column(String(255), default="")
    candidate_phone = Column(String(100), default="")
    file_name = Column(String(255), default="resume.pdf")
    
    job_title = Column(String(255), default="Target Role")
    job_company = Column(String(255), default="Target Company")
    
    overall_score = Column(Float, default=0.0)
    match_rating = Column(String(100), default="Needs Optimization")
    
    skills_score = Column(Float, default=0.0)
    similarity_score = Column(Float, default=0.0)
    section_score = Column(Float, default=0.0)
    metrics_score = Column(Float, default=0.0)
    
    extracted_skills = Column(Text, default="[]")   # JSON list
    matching_skills = Column(Text, default="[]")    # JSON list
    missing_skills = Column(Text, default="[]")     # JSON list
    additional_skills = Column(Text, default="[]")  # JSON list
    
    parsed_sections = Column(Text, default="{}")    # JSON object
    recommendations = Column(Text, default="[]")    # JSON list
    score_breakdown = Column(Text, default="{}")    # JSON object
    
    raw_resume_text = Column(Text, default="")
    raw_job_description = Column(Text, default="")


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    company = Column(String(255), index=True, nullable=False)
    company_logo = Column(String(500), default="")
    company_id = Column(String(100), index=True, default="")
    
    location = Column(String(255), default="Remote")
    city = Column(String(100), default="")
    country = Column(String(100), default="Global")
    work_mode = Column(String(50), default="Remote", index=True)  # "Remote" | "Hybrid" | "On-site"
    
    role_category = Column(String(100), default="Software Engineering", index=True)
    experience_level = Column(String(50), default="Mid-level", index=True)  # "Internship" | "Fresher / Entry" | "Junior" | "Mid-level" | "Senior" | "Lead / Principal"
    employment_type = Column(String(50), default="Full-time", index=True)  # "Full-time" | "Part-time" | "Internship" | "Contract"
    
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(20), default="USD")
    salary_text = Column(String(100), default="")
    
    skills = Column(Text, default="[]")  # JSON list of extracted skills
    description = Column(Text, default="")  # Full job description
    url = Column(String(1000), default="")  # Direct application link
    source = Column(String(100), default="Verified Career Portal")  # "Remotive" | "Greenhouse" | "Arbeitnow" | "The Muse" | "Adzuna"
    
    posted_date = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(String(100), primary_key=True, index=True)  # e.g. "google", "microsoft", "tcs"
    name = Column(String(255), index=True, nullable=False)
    logo = Column(String(500), default="")
    industry = Column(String(100), default="Technology", index=True)
    headquarters = Column(String(255), default="")
    locations = Column(Text, default="[]")  # JSON list of offices
    website = Column(String(500), default="")
    career_page = Column(String(500), default="")
    description = Column(Text, default="")
    size = Column(String(100), default="10,000+ employees")
    founded_year = Column(Integer, nullable=True)
    openings_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
