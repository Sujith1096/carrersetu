from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), default="")
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Isolated analysis reports belonging exclusively to this user
    analyses = relationship("AnalysisRecord", back_populates="owner", cascade="all, delete-orphan")


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Ownership association (Strict authorization)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    owner = relationship("User", back_populates="analyses")

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
    experience_level = Column(String(50), default="Mid-level", index=True)
    employment_type = Column(String(50), default="Full-time", index=True)
    
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(20), default="USD")
    salary_text = Column(String(100), default="")
    
    skills = Column(Text, default="[]")  # JSON list of extracted skills
    description = Column(Text, default="")  # Full job description
    url = Column(String(1000), default="")  # Direct application link
    source = Column(String(100), default="Verified Career Portal")
    is_demo = Column(Boolean, default=False, index=True)  # Distinguish curated demo from live
    
    posted_date = Column(DateTime, default=datetime.utcnow, index=True)
    last_synced_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(String(100), primary_key=True, index=True)
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


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"

    id = Column(String(50), primary_key=True, default="jobs_sync")
    last_sync_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    synced_by = Column(String(100), default="system")
    total_fetched = Column(Integer, default=0)
    total_added = Column(Integer, default=0)
    message = Column(String(500), default="")
