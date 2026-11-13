import re
import numpy as np
from typing import List, Dict, Tuple, Any, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.skill_bank import ALL_SKILLS, CANONICAL_SKILL_MAP

# High-impact ATS action verbs
ACTION_VERBS = {
    "spearheaded", "architected", "engineered", "orchestrated", "deployed",
    "optimized", "streamlined", "accelerated", "designed", "developed",
    "implemented", "mentored", "directed", "formulated", "transformed",
    "automated", "consolidated", "negotiated", "pioneered", "enhanced",
    "generated", "reduced", "increased", "maximized", "minimized",
    "debugged", "refactored", "integrated", "executed", "collaborated"
}

# English stop words list
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

# Regex for metrics / impact
METRIC_PATTERNS = [
    r"\b\d+(?:\.\d+)?%",                                    # 35%, 12.5%
    r"\$\s*\d+(?:,\d{3})*(?:\.\d+)?(?:\s*[kKmMbB])?",      # $500k, $1.2M, $50,000
    r"\b\d+\s*(?:k|m|b|million|billion|thousand)\b",       # 50k, 2 million
    r"\b\d+[\+,\d]*\s*(?:users|clients|customers|requests|transactions|rps|tps|engineers|developers|members|stars|contributors|hours|minutes|seconds|ms)\b", # 150,000 users, 2M+ requests
    r"\b\d+(?:\.\d+)?\s*(?:x|fold)\s*(?:faster|speedup|improvement|growth|reduction)?\b" # 10x faster
]

def preprocess_text(text: str) -> str:
    """Normalize text for ML vectorization."""
    if not text:
        return ""
    text_lower = text.lower()
    # Replace slashes and hyphens with spaces for better tokenization
    cleaned = re.sub(r"[/\-_]", " ", text_lower)
    # Remove special punctuation but keep alphanumeric and spaces
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    tokens = [w for w in cleaned.split() if w not in STOP_WORDS and len(w) > 1]
    return " ".join(tokens)

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from text using boundary-aware regex matching
    and canonical deduplication.
    """
    if not text:
        return []
    
    found_skills: Set[str] = set()
    text_clean = " " + text.replace("\n", " ") + " "
    
    # Sort skills by length descending to match longest phrases first (e.g. "Natural Language Processing" before "NLP")
    sorted_skills = sorted(ALL_SKILLS, key=len, reverse=True)
    
    for skill in sorted_skills:
        # Build regex with boundary handling
        # Escape special regex chars in skill names (e.g. C++, C#, .NET, CI/CD)
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_clean, re.IGNORECASE):
            canonical = CANONICAL_SKILL_MAP.get(skill.lower(), skill)
            found_skills.add(canonical)
            
    # Also check specific multi-word / punctuation cases (e.g., C++, C#, .NET, CI/CD)
    special_cases = {
        r"\bc\+\+\b": "C++",
        r"\bc#\b": "C#",
        r"\.net\b": "ASP.NET Core",
        r"\bci\s*/\s*cd\b": "CI/CD",
        r"\bui\s*/\s*ux\b": "UI/UX",
        r"\bnode(?:\.js)?\b": "Node.js",
        r"\breact(?:\.js)?\b": "React",
        r"\bvue(?:\.js)?\b": "Vue",
        r"\bnext(?:\.js)?\b": "Next.js"
    }
    for pat, name in special_cases.items():
        if re.search(pat, text_clean, re.IGNORECASE):
            found_skills.add(name)

    return sorted(list(found_skills))

def compute_tfidf_similarity(resume_text: str, jd_text: str) -> Tuple[float, List[Tuple[str, float]]]:
    """
    Compute TF-IDF vectorization and Cosine Similarity between resume and JD.
    Returns calibrated cosine similarity (0 to 100) and top matching keyword terms.
    """
    clean_resume = preprocess_text(resume_text)
    clean_jd = preprocess_text(jd_text)
    
    if not clean_resume or not clean_jd:
        return 0.0, []
        
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        raw_cosine = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        
        # Calibrate raw cosine similarity
        # Natural language documents rarely exceed 0.5-0.6 raw cosine similarity even when highly matched.
        # We map raw_cosine [0.0, 0.50] to [0.0, 95.0] with smooth saturation.
        if raw_cosine <= 0.05:
            scaled_similarity = raw_cosine * 300  # 0 to 15
        elif raw_cosine <= 0.25:
            scaled_similarity = 15.0 + ((raw_cosine - 0.05) / 0.20) * 45.0  # 15 to 60
        elif raw_cosine <= 0.45:
            scaled_similarity = 60.0 + ((raw_cosine - 0.25) / 0.20) * 28.0  # 60 to 88
        else:
            scaled_similarity = min(98.0, 88.0 + ((raw_cosine - 0.45) / 0.25) * 10.0)

        # Extract top shared n-grams
        feature_names = np.array(vectorizer.get_feature_names_out())
        resume_vec = tfidf_matrix[0].toarray().flatten()
        jd_vec = tfidf_matrix[1].toarray().flatten()
        
        # Element-wise product shows terms that contributed most to similarity
        overlap_weights = resume_vec * jd_vec
        top_indices = np.argsort(overlap_weights)[::-1]
        
        top_shared_terms = []
        for idx in top_indices:
            if overlap_weights[idx] > 0 and len(top_shared_terms) < 10:
                top_shared_terms.append((feature_names[idx], float(overlap_weights[idx])))
                
        return round(scaled_similarity, 1), top_shared_terms
        
    except Exception as e:
        return 0.0, []

def detect_action_verbs(text: str) -> List[str]:
    """Detect presence of strong ATS action verbs."""
    text_lower = text.lower()
    words = set(re.findall(r"\b[a-z]{3,}\b", text_lower))
    found = [v.capitalize() for v in ACTION_VERBS if v in words]
    return sorted(found)

def detect_quantified_metrics(text: str) -> int:
    """Count occurrences of measurable results and metrics."""
    total_metrics = 0
    for pat in METRIC_PATTERNS:
        matches = re.findall(pat, text, re.IGNORECASE)
        total_metrics += len(matches)
    return total_metrics

def calculate_ats_score(
    resume_text: str,
    jd_text: str,
    parsed_sections: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate comprehensive ATS score with explainable component weights.
    """
    # 1. Skills Extraction
    resume_skills = extract_skills_from_text(resume_text)
    jd_skills = extract_skills_from_text(jd_text)
    
    matching_skills = sorted(list(set(resume_skills).intersection(set(jd_skills))))
    missing_skills = sorted(list(set(jd_skills).difference(set(resume_skills))))
    additional_skills = sorted(list(set(resume_skills).difference(set(jd_skills))))
    
    # 2. Skills Score Calculation (40% weight)
    if jd_skills:
        skills_ratio = len(matching_skills) / len(jd_skills)
        skills_score = min(100.0, skills_ratio * 100.0)
    else:
        # If JD has no recognized skills in bank, score based on candidate skill breadth
        skills_score = min(90.0, len(resume_skills) * 8.0)
    skills_score = round(skills_score, 1)
    
    # 3. TF-IDF & Cosine Similarity (25% weight)
    similarity_score, top_terms = compute_tfidf_similarity(resume_text, jd_text)
    
    # 4. Measurable Metrics & Action Verbs (20% weight)
    action_verbs = detect_action_verbs(resume_text)
    metrics_count = detect_quantified_metrics(resume_text)
    
    # Action verbs score (max 10 verbs = 50 pts)
    verb_score = min(50.0, len(action_verbs) * 5.0)
    # Metrics score (max 6 metrics = 50 pts)
    metric_score = min(50.0, metrics_count * 8.5)
    metrics_combined_score = round(verb_score + metric_score, 1)
    
    # 5. Section Completeness (15% weight)
    # Expected key sections: Experience (30), Skills (25), Education (20), Projects (15), Summary (10)
    section_points = 0.0
    if parsed_sections.get("experience", {}).get("present", False):
        section_points += 30.0
    if parsed_sections.get("skills", {}).get("present", False) or len(resume_skills) >= 4:
        section_points += 25.0
    if parsed_sections.get("education", {}).get("present", False):
        section_points += 20.0
    if parsed_sections.get("projects", {}).get("present", False):
        section_points += 15.0
    if parsed_sections.get("summary", {}).get("present", False):
        section_points += 10.0
    section_score = round(section_points, 1)
    
    # Overall Score formula (Weighted Composite)
    overall_score = round(
        (skills_score * 0.40) +
        (similarity_score * 0.25) +
        (metrics_combined_score * 0.20) +
        (section_score * 0.15),
        1
    )
    overall_score = max(5.0, min(99.0, overall_score))
    
    # Match Rating categorization
    if overall_score >= 85.0:
        match_rating = "Excellent Match"
    elif overall_score >= 70.0:
        match_rating = "Strong Match"
    elif overall_score >= 55.0:
        match_rating = "Moderate Match"
    else:
        match_rating = "Needs Optimization"
        
    explanation = {
        "skills": f"Matched {len(matching_skills)} of {len(jd_skills)} required technical skills from the target job profile.",
        "similarity": f"TF-IDF cosine similarity model scored content alignment at {similarity_score}%.",
        "metrics": f"Detected {len(action_verbs)} high-impact action verbs and {metrics_count} quantified performance metrics.",
        "sections": f"Resume architecture is {int(section_score)}% complete across standard ATS sections (Experience, Skills, Education, Projects)."
    }
    
    return {
        "overall_score": overall_score,
        "match_rating": match_rating,
        "skills_score": skills_score,
        "similarity_score": similarity_score,
        "metrics_score": metrics_combined_score,
        "section_score": section_score,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "action_verbs": action_verbs,
        "metrics_count": metrics_count,
        "top_terms": top_terms,
        "explanation": explanation
    }
