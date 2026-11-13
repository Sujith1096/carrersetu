from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AnalyzeTextRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: Optional[str] = "Target Role"
    job_company: Optional[str] = "Company"
    file_name: Optional[str] = "pasted_resume.txt"

class RecommendationItem(BaseModel):
    category: str  # "skills", "metrics", "formatting", "experience", "keywords"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    suggestion: str

class ScoreBreakdown(BaseModel):
    skills_score: float
    similarity_score: float
    section_score: float
    metrics_score: float
    overall_score: float
    match_rating: str
    skills_weight: float = 0.40
    similarity_weight: float = 0.25
    metrics_weight: float = 0.20
    section_weight: float = 0.15
    explanation: Dict[str, str]

class AnalysisResponse(BaseModel):
    id: Optional[int] = None
    created_at: Optional[str] = None
    candidate_name: str
    candidate_email: str
    candidate_phone: str
    candidate_links: Dict[str, str] = {}
    file_name: str
    job_title: str
    job_company: str
    overall_score: float
    match_rating: str
    score_breakdown: ScoreBreakdown
    extracted_skills: List[str]
    matching_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str]
    parsed_sections: Dict[str, Any]
    recommendations: List[RecommendationItem]
    word_count_resume: int
    word_count_jd: int
    quantified_metrics_count: int
    action_verbs_found: List[str]
    raw_resume_text: Optional[str] = None
    raw_job_description: Optional[str] = None

class HistoryItem(BaseModel):
    id: int
    created_at: str
    candidate_name: str
    candidate_email: str
    job_title: str
    job_company: str
    file_name: str
    overall_score: float
    match_rating: str
    matching_skills_count: int
    missing_skills_count: int

class StatsResponse(BaseModel):
    total_analyses: int
    average_score: float
    highest_score: float
    lowest_score: float
    score_distribution: Dict[str, int]
    top_in_demand_skills: List[Dict[str, Any]]
    top_missing_skills: List[Dict[str, Any]]
    recent_history: List[HistoryItem]

class SampleDataResponse(BaseModel):
    id: str
    title: str
    company: str
    department: str
    experience_level: str
    description: str
    key_skills: List[str]

# =========================================================================
# GLOBAL JOBS & COMPANIES EXPLORER SCHEMAS
# =========================================================================

class JobItem(BaseModel):
    id: str
    title: str
    company: str
    company_logo: str = ""
    company_id: str = ""
    location: str = "Remote"
    city: str = ""
    country: str = "Global"
    work_mode: str = "Remote"
    role_category: str = "Software Engineering"
    experience_level: str = "Mid-level"
    employment_type: str = "Full-time"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    salary_text: str = ""
    skills: List[str] = []
    description: str = ""
    url: str = ""
    source: str = "Verified Career Portal"
    posted_date: str = ""
    is_active: bool = True

class JobListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    jobs: List[JobItem]

class CompanyItem(BaseModel):
    id: str
    name: str
    logo: str = ""
    industry: str = "Technology"
    headquarters: str = ""
    locations: List[str] = []
    website: str = ""
    career_page: str = ""
    description: str = ""
    size: str = "10,000+ employees"
    founded_year: Optional[int] = None
    openings_count: int = 0
    is_featured: bool = False

class CompanyListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    companies: List[CompanyItem]

class CompanyDetailResponse(BaseModel):
    company: CompanyItem
    jobs: List[JobItem]

class JobFilterOptionsResponse(BaseModel):
    roles: List[str]
    companies: List[str]
    locations: List[str]
    experience_levels: List[str]
    work_modes: List[str]
    employment_types: List[str]
    popular_skills: List[str]

class SyncJobsResponse(BaseModel):
    status: str
    message: str
    fetched: int
    added: int
    total_active_jobs: int
