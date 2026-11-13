from typing import List, Dict, Any
from app.schemas import RecommendationItem

def generate_recommendations(
    scoring_data: Dict[str, Any],
    parsed_sections: Dict[str, Any],
    candidate_links: Dict[str, str]
) -> List[RecommendationItem]:
    """
    Generate targeted, actionable recommendations based on ATS evaluation.
    """
    recs: List[RecommendationItem] = []
    
    missing_skills = scoring_data.get("missing_skills", [])
    matching_skills = scoring_data.get("matching_skills", [])
    metrics_count = scoring_data.get("metrics_count", 0)
    action_verbs = scoring_data.get("action_verbs", [])
    similarity_score = scoring_data.get("similarity_score", 0.0)
    
    # 1. Missing Skills (Highest Priority)
    if missing_skills:
        top_missing = missing_skills[:5]
        skills_str = ", ".join(top_missing)
        recs.append(RecommendationItem(
            category="skills",
            priority="high",
            title=f"Incorporate Missing Critical Skills ({len(missing_skills)} identified)",
            description=f"The job description highlights requirements that were not found in your resume: {skills_str}.",
            suggestion=f"If you have hands-on experience with {skills_str}, explicitly feature them in your Skills section and highlight how you applied them in your Experience bullets."
        ))
        
        if len(missing_skills) > 5:
            secondary_missing = missing_skills[5:10]
            recs.append(RecommendationItem(
                category="skills",
                priority="medium",
                title="Secondary Skill Alignment",
                description=f"Additional keywords from the job description: {', '.join(secondary_missing)}.",
                suggestion="Consider adding relevant certifications, course projects, or tooling exposure for these secondary competencies."
            ))

    # 2. Quantified Achievements & Business Impact
    if metrics_count < 3:
        recs.append(RecommendationItem(
            category="metrics",
            priority="high",
            title="Quantify Project Outcomes & Business Metrics",
            description=f"Only {metrics_count} quantified metrics (percentages, numbers, or scale) were detected.",
            suggestion="Rewrite passive bullet points into the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'. Example: 'Reduced API response latency by 35% across 2M daily requests by implementing Redis caching'."
        ))
    elif metrics_count < 6:
        recs.append(RecommendationItem(
            category="metrics",
            priority="medium",
            title="Strengthen Impact Metrics in Recent Experience",
            description=f"Detected {metrics_count} metrics. High-scoring ATS resumes typically feature at least 1-2 numbers per role.",
            suggestion="Add metrics such as team size mentored, deployment frequency improvements, cost savings, or user base growth to your most recent positions."
        ))

    # 3. Action Verbs & Leadership Phrasing
    if len(action_verbs) < 5:
        recs.append(RecommendationItem(
            category="keywords",
            priority="high",
            title="Elevate Responsibility Phrasing with Power Verbs",
            description="Detected limited high-impact action verbs. Avoid passive phrasing like 'responsible for' or 'assisted with'.",
            suggestion="Begin bullet points with decisive action verbs like 'Architected', 'Spearheaded', 'Orchestrated', 'Optimized', and 'Streamlined' to capture ATS parser interest."
        ))
    else:
        recs.append(RecommendationItem(
            category="keywords",
            priority="low",
            title="Maintain Strong Active Phrasing",
            description=f"Great job using {len(action_verbs)} power verbs ({', '.join(action_verbs[:4])}).",
            suggestion="Ensure these verbs are varied across entries and followed immediately by tangible business results."
        ))

    # 4. Section Structure & Contact Links
    if not parsed_sections.get("projects", {}).get("present", False):
        recs.append(RecommendationItem(
            category="formatting",
            priority="medium",
            title="Add a Dedicated Projects Section",
            description="No dedicated 'Projects' or 'Technical Initiatives' section header was detected by the parser.",
            suggestion="Add 2-3 highlighted projects showcasing your full technical stack, system architecture decisions, and live demo links."
        ))
        
    if not candidate_links.get("github"):
        recs.append(RecommendationItem(
            category="formatting",
            priority="medium",
            title="Include GitHub Profile Link",
            description="No GitHub profile URL was detected in the contact header.",
            suggestion="Add your clean GitHub profile link near your email. Technical recruiters frequently verify commit activity and repository quality."
        ))
        
    if not candidate_links.get("linkedin"):
        recs.append(RecommendationItem(
            category="formatting",
            priority="medium",
            title="Include LinkedIn Profile URL",
            description="No customized LinkedIn vanity URL was detected in the header.",
            suggestion="Include a customized LinkedIn profile link (e.g., linkedin.com/in/yourname) in the header for fast recruiter vetting."
        ))

    # 5. TF-IDF Contextual Alignment
    if similarity_score < 60.0:
        recs.append(RecommendationItem(
            category="content",
            priority="high",
            title="Align Phrasing with Target Role Terminology",
            description=f"Your semantic similarity score is {similarity_score}%, indicating a terminology mismatch with the job posting.",
            suggestion="Adopt specific terminology from the job description. For example, if the JD asks for 'microservices orchestration' and you wrote 'distributed services', adapt your wording to match."
        ))

    return recs
