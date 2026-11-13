import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.skill_bank import ALL_SKILLS, get_skill_category
from app.services.ml_engine import (
    preprocess_text,
    extract_skills_from_text,
    compute_tfidf_similarity,
    detect_action_verbs,
    detect_quantified_metrics,
    calculate_ats_score
)
from app.services.pdf_parser import extract_text_from_pdf_bytes, parse_contact_info, segment_resume_sections
from app.data.sample_data import SAMPLE_JOBS, SAMPLE_RESUME_TEXT

def run_all_tests():
    print("========================================")
    print("Testing CareerSetu ML & Backend Engine")
    print("========================================")
    
    # 1. Test Skill Bank
    assert len(ALL_SKILLS) > 100, f"Expected >100 skills, found {len(ALL_SKILLS)}"
    print(f"[PASS] Skill Bank loaded {len(ALL_SKILLS)} unique skills across 9 categories.")

    # 2. Test Text Preprocessing
    sample_text = "Experienced Senior Developer building React.js and Python micro-services!"
    cleaned = preprocess_text(sample_text)
    assert "experienced" in cleaned and "react" in cleaned and "python" in cleaned
    print(f"[PASS] Text preprocessing cleaned: '{cleaned}'")

    # 3. Test Skill Extraction
    extracted = extract_skills_from_text(SAMPLE_RESUME_TEXT)
    assert "Python" in extracted, "Python should be detected"
    assert "React" in extracted, "React should be detected"
    assert "FastAPI" in extracted, "FastAPI should be detected"
    assert "Docker" in extracted, "Docker should be detected"
    print(f"[PASS] Skill extraction extracted {len(extracted)} skills from sample resume: {extracted[:6]}...")

    # 4. Test TF-IDF and Cosine Similarity
    job = SAMPLE_JOBS[0]
    sim_score, top_terms = compute_tfidf_similarity(SAMPLE_RESUME_TEXT, job["description"])
    assert 40.0 <= sim_score <= 100.0, f"Unexpected similarity score: {sim_score}"
    print(f"[PASS] TF-IDF Cosine similarity score: {sim_score}% with top terms: {[t[0] for t in top_terms[:4]]}")

    # 5. Test Action Verbs & Metrics
    verbs = detect_action_verbs(SAMPLE_RESUME_TEXT)
    metrics_count = detect_quantified_metrics(SAMPLE_RESUME_TEXT)
    assert len(verbs) >= 4, f"Expected >=4 verbs, found {len(verbs)}"
    assert metrics_count >= 3, f"Expected >=3 metrics, found {metrics_count}"
    print(f"[PASS] Detected {len(verbs)} action verbs: {verbs[:5]} and {metrics_count} metrics.")

    # 6. Test ATS Score Calculation
    sections = segment_resume_sections(SAMPLE_RESUME_TEXT)
    ats_result = calculate_ats_score(SAMPLE_RESUME_TEXT, job["description"], sections)
    assert "overall_score" in ats_result
    assert ats_result["overall_score"] > 60.0
    print(f"[PASS] ATS Overall Score: {ats_result['overall_score']}/100, Rating: {ats_result['match_rating']}")
    print(f"       Skills Match: {ats_result['skills_score']}%, TF-IDF Sim: {ats_result['similarity_score']}%")

    # 7. Test PDF file extraction
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Alex_Rivera_Resume.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        extracted_pdf_text = extract_text_from_pdf_bytes(pdf_bytes)
        assert len(extracted_pdf_text) > 100
        name, email, phone, links = parse_contact_info(extracted_pdf_text)
        assert "Alex" in name or "Rivera" in name
        assert "alex.rivera@example.com" in email
        print(f"[PASS] PyMuPDF extracted {len(extracted_pdf_text)} chars from generated PDF. Parsed: Name='{name}', Email='{email}', Phone='{phone}'.")
    else:
        print("[WARN] Sample PDF not found for direct test.")

    print("\n>>> ALL TESTS PASSED SUCCESSFULLY! <<<\n")

if __name__ == "__main__":
    run_all_tests()
