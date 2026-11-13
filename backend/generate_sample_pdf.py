import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from app.data.sample_data import SAMPLE_RESUME_TEXT

def create_sample_pdf(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles matching our premium theme
    dark_green = colors.HexColor("#123C2E")
    gold_accent = colors.HexColor("#A37D24")
    dark_gray = colors.HexColor("#2B2D2F")
    
    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=dark_green
    )
    
    subtitle_style = ParagraphStyle(
        "ResumeSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=gold_accent
    )

    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568")
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=dark_green,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=dark_gray
    )

    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        leftIndent=12,
        firstLineIndent=-8,
        textColor=dark_gray,
        spaceAfter=2
    )

    story = []

    # Header
    story.append(Paragraph("ALEX RIVERA", title_style))
    story.append(Paragraph("Senior Full Stack & Cloud Software Engineer", subtitle_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("San Francisco, CA &bull; (415) 555-0192 &bull; alex.rivera@example.com &bull; github.com/alexrivera &bull; linkedin.com/in/alexrivera-dev", contact_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=dark_green, spaceAfter=8))

    # Summary
    story.append(Paragraph("SUMMARY", section_heading))
    story.append(Paragraph("Results-driven Senior Full Stack Engineer with 5+ years of experience designing scalable web applications, distributed APIs, and cloud services. Proven track record of improving system performance by 45%, architecting microservices handling 2M+ daily requests, and leading cross-functional engineering teams.", body_style))
    story.append(Spacer(1, 8))

    # Core Competencies & Skills
    story.append(Paragraph("TECHNICAL SKILLS", section_heading))
    skills_text = (
        "<b>Languages:</b> Python, JavaScript, TypeScript, SQL, Bash<br/>"
        "<b>Frontend:</b> React, Next.js, Redux, Tailwind CSS, HTML5, CSS3, Vite, UI/UX<br/>"
        "<b>Backend & APIs:</b> FastAPI, Node.js, Express, REST API, GraphQL, Microservices, System Design<br/>"
        "<b>Databases & Cloud:</b> PostgreSQL, Redis, MongoDB, Docker, Kubernetes, AWS, CI/CD, GitHub Actions, Linux<br/>"
        "<b>Testing & Tools:</b> Pytest, Jest, Unit Testing, Git, Agile, Scrum"
    )
    story.append(Paragraph(skills_text, body_style))
    story.append(Spacer(1, 8))

    # Professional Experience
    story.append(Paragraph("WORK EXPERIENCE", section_heading))
    
    # Job 1
    story.append(Paragraph("<b>Senior Full Stack Engineer</b> &bull; Apex Cloud Solutions, San Francisco, CA <i>(June 2022 &ndash; Present)</i>", body_style))
    story.append(Paragraph("&bull; Architected and deployed a multi-tenant enterprise dashboard using React, TypeScript, Tailwind CSS, and FastAPI, serving 150,000 active users.", bullet_style))
    story.append(Paragraph("&bull; Redesigned backend PostgreSQL database schema and introduced Redis caching layer, reducing API endpoint latency by 45% and query execution time by 60%.", bullet_style))
    story.append(Paragraph("&bull; Engineered automated CI/CD deployment pipelines using Docker and GitHub Actions, cutting production release cycles from 3 hours to 18 minutes.", bullet_style))
    story.append(Paragraph("&bull; Spearheaded migration of legacy monolithic services into containerized microservices orchestrated on AWS ECS and Kubernetes.", bullet_style))
    story.append(Paragraph("&bull; Mentored a cohort of 5 junior and mid-level software engineers through structured pair programming and weekly architectural code reviews.", bullet_style))
    story.append(Spacer(1, 6))

    # Job 2
    story.append(Paragraph("<b>Software Engineer</b> &bull; Horizon Tech Labs, Austin, TX <i>(August 2020 &ndash; May 2022)</i>", body_style))
    story.append(Paragraph("&bull; Developed responsive web applications using React, Redux, and Node.js/Express, increasing user retention by 28%.", bullet_style))
    story.append(Paragraph("&bull; Integrated RESTful APIs and secure OAuth 2.0 authentication for fintech payment processing services.", bullet_style))
    story.append(Paragraph("&bull; Automated end-to-end testing suites using Jest and Pytest, boosting code test coverage from 52% to 88%.", bullet_style))
    story.append(Paragraph("&bull; Collaborated closely with UI/UX designers and product owners in bi-weekly agile Scrum sprints.", bullet_style))
    story.append(Spacer(1, 8))

    # Key Technical Projects
    story.append(Paragraph("PROJECTS", section_heading))
    story.append(Paragraph("<b>CareerSetu &ndash; AI Career Intelligence Platform</b> | <i>React, Tailwind CSS, FastAPI, Scikit-learn, PyMuPDF</i>", body_style))
    story.append(Paragraph("&bull; Built an end-to-end career platform utilizing TF-IDF vectorization and cosine similarity scoring for resume-to-job matching.", bullet_style))
    story.append(Paragraph("&bull; Engineered automated PDF parsing, section extraction, and interactive visual skill gap analysis.", bullet_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>CloudScale &ndash; Distributed Telemetry Collector</b> | <i>Python, Node.js, WebSockets, Redis</i>", body_style))
    story.append(Paragraph("&bull; Created a lightweight metrics aggregator handling 50k events/second; attracted 600+ GitHub stars.", bullet_style))
    story.append(Spacer(1, 8))

    # Education & Certifications
    story.append(Paragraph("EDUCATION & CERTIFICATIONS", section_heading))
    story.append(Paragraph("<b>Bachelor of Science in Computer Science</b> &bull; University of California, Berkeley <i>(2016 &ndash; 2020)</i>", body_style))
    story.append(Paragraph("<b>AWS Certified Solutions Architect &ndash; Associate</b> <i>(2023)</i>", body_style))

    doc.build(story)
    print(f"Sample PDF resume successfully generated at: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    out_file = os.path.join(out_dir, "Alex_Rivera_Resume.pdf")
    create_sample_pdf(out_file)
