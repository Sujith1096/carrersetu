import re
from typing import Dict, Any, Tuple
import pymupdf as fitz  # PyMuPDF

SECTION_PATTERNS = {
    "experience": [
        r"(?:work\s+)?experience",
        r"employment\s+history",
        r"professional\s+experience",
        r"work\s+history",
        r"career\s+summary",
        r"relevant\s+experience"
    ],
    "education": [
        r"education",
        r"academic\s+background",
        r"academic\s+history",
        r"educational\s+qualifications",
        r"degrees?"
    ],
    "skills": [
        r"(?:technical\s+)?skills",
        r"core\s+competencies",
        r"technologies",
        r"skills\s+&\s+expertise",
        r"tools\s+&\s+technologies",
        r"technical\s+proficiencies"
    ],
    "projects": [
        r"projects?",
        r"personal\s+projects",
        r"academic\s+projects",
        r"key\s+projects",
        r"technical\s+projects"
    ],
    "certifications": [
        r"certifications?",
        r"certificates?",
        r"licenses\s+&\s+certifications",
        r"credentials"
    ],
    "summary": [
        r"summary",
        r"professional\s+summary",
        r"executive\s+summary",
        r"about\s+me",
        r"profile",
        r"objective"
    ]
}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LINKEDIN_REGEX = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?", re.IGNORECASE)
GITHUB_REGEX = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?", re.IGNORECASE)
URL_REGEX = re.compile(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)", re.IGNORECASE)

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract full clean text from PDF bytes using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}")
    
    if doc.is_encrypted:
        raise ValueError("Password protected PDF files are not supported.")
    
    extracted_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text:
            extracted_text.append(text)
    
    full_text = "\n".join(extracted_text).strip()
    if not full_text or len(full_text.strip()) < 30:
        raise ValueError(
            "Could not extract readable text from this PDF. It appears to be an image-only scanned document or empty. "
            "Please upload a text-based PDF or switch to the 'Paste Resume Text' tab to analyze immediately."
        )
    
    return full_text

def parse_contact_info(text: str) -> Tuple[str, str, str, Dict[str, str]]:
    """Extract candidate name, email, phone and links."""
    # Email
    emails = EMAIL_REGEX.findall(text)
    email = emails[0] if emails else ""
    
    # Phone
    phones = PHONE_REGEX.findall(text)
    phone = phones[0] if phones else ""
    
    # Links
    links = {}
    linkedin_matches = LINKEDIN_REGEX.findall(text)
    if linkedin_matches:
        links["linkedin"] = linkedin_matches[0]
        
    github_matches = GITHUB_REGEX.findall(text)
    if github_matches:
        links["github"] = github_matches[0]
        
    all_urls = URL_REGEX.findall(text)
    for u in all_urls:
        if "linkedin" not in u.lower() and "github" not in u.lower():
            links["portfolio"] = u
            break

    # Candidate Name Extraction
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    candidate_name = "Candidate"
    
    ignore_headers = {"resume", "curriculum vitae", "cv", "portfolio", "profile", "contact", "email"}
    for line in lines[:5]:
        clean_line = re.sub(r"[^a-zA-Z\s]", "", line).strip()
        words = clean_line.split()
        if 2 <= len(words) <= 4:
            if clean_line.lower() not in ignore_headers and not any(w.lower() in ignore_headers for w in words):
                candidate_name = clean_line.title()
                break
                
    return candidate_name, email, phone, links

def segment_resume_sections(text: str) -> Dict[str, Any]:
    """Segment resume text into recognized standard sections."""
    sections: Dict[str, Any] = {
        "summary": {"present": False, "content": ""},
        "experience": {"present": False, "content": ""},
        "education": {"present": False, "content": ""},
        "skills": {"present": False, "content": ""},
        "projects": {"present": False, "content": ""},
        "certifications": {"present": False, "content": ""}
    }
    
    lines = text.split("\n")
    current_section = None
    section_buffers = {k: [] for k in sections}
    
    compiled_patterns = {}
    for sec_name, pats in SECTION_PATTERNS.items():
        compiled_patterns[sec_name] = [
            re.compile(rf"^\s*(?:[\#\*\-•]?\s*)*(?:{p})\s*[:\-_]?\s*$", re.IGNORECASE)
            for p in pats
        ]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_section:
                section_buffers[current_section].append("")
            continue
            
        matched_section = None
        # Check if line is a section header (short line, usually <= 40 chars)
        if len(stripped) <= 45:
            for sec_name, regex_list in compiled_patterns.items():
                if any(r.match(stripped) for r in regex_list):
                    matched_section = sec_name
                    break
        
        if matched_section:
            current_section = matched_section
            sections[current_section]["present"] = True
        elif current_section:
            section_buffers[current_section].append(line)
            
    for sec_name in sections:
        content = "\n".join(section_buffers[sec_name]).strip()
        if content:
            sections[sec_name]["present"] = True
            sections[sec_name]["content"] = content
            
    return sections
