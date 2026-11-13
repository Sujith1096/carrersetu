import html
import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from app.models import JobListing, CompanyProfile
from app.services.ml_engine import extract_skills_from_text
from app.services.skill_bank import ALL_SKILLS

def _clean_html_description(html_text: str) -> str:
    if not html_text:
        return ""
    text = html.unescape(html_text)
    text = re.sub(r"<(?:p|div|br|li|h[1-6])[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return text

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CareerSetu/1.0"

# =========================================================================
# GLOBAL COMPANIES TAXONOMY (40+ Global & Indian Leaders)
# =========================================================================

INITIAL_COMPANIES = [
    {
        "id": "google",
        "name": "Google",
        "logo": "https://www.google.com/favicon.ico",
        "industry": "Big Tech / Search & Cloud",
        "headquarters": "Mountain View, CA, USA",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Mountain View, USA", "New York, USA", "London, UK", "Remote"],
        "website": "https://about.google",
        "career_page": "https://careers.google.com",
        "description": "Global technology leader in search, cloud computing (GCP), advertising, AI research (DeepMind), and enterprise software.",
        "size": "180,000+ employees",
        "founded_year": 1998,
        "is_featured": True
    },
    {
        "id": "microsoft",
        "name": "Microsoft",
        "logo": "https://www.microsoft.com/favicon.ico",
        "industry": "Enterprise Software & Cloud",
        "headquarters": "Redmond, WA, USA",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Noida, India", "Redmond, USA", "Dublin, Ireland", "Remote"],
        "website": "https://www.microsoft.com",
        "career_page": "https://careers.microsoft.com",
        "description": "Pioneering enterprise computing, Microsoft Azure cloud, developer tools (GitHub, VS Code), and OpenAI partnerships.",
        "size": "220,000+ employees",
        "founded_year": 1975,
        "is_featured": True
    },
    {
        "id": "amazon",
        "name": "Amazon",
        "logo": "https://www.amazon.com/favicon.ico",
        "industry": "E-Commerce & Cloud Infrastructure",
        "headquarters": "Seattle, WA, USA",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Chennai, India", "Seattle, USA", "Luxembourg", "Remote"],
        "website": "https://www.amazon.com",
        "career_page": "https://www.amazon.jobs",
        "description": "World's leading e-commerce and cloud infrastructure platform via Amazon Web Services (AWS), AI devices, and logistics.",
        "size": "1,500,000+ employees",
        "founded_year": 1994,
        "is_featured": True
    },
    {
        "id": "meta",
        "name": "Meta",
        "logo": "https://about.meta.com/favicon.ico",
        "industry": "Social Technology & AI",
        "headquarters": "Menlo Park, CA, USA",
        "locations": ["Bengaluru, India", "Gurgaon, India", "Menlo Park, USA", "London, UK", "Singapore", "Remote"],
        "website": "https://about.meta.com",
        "career_page": "https://www.metacareers.com",
        "description": "Building social platforms (Instagram, WhatsApp, Facebook), PyTorch open-source AI, Llama models, and spatial computing.",
        "size": "67,000+ employees",
        "founded_year": 2004,
        "is_featured": True
    },
    {
        "id": "apple",
        "name": "Apple",
        "logo": "https://www.apple.com/favicon.ico",
        "industry": "Consumer Tech & Silicon",
        "headquarters": "Cupertino, CA, USA",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Cupertino, USA", "Cork, Ireland", "Tokyo, Japan"],
        "website": "https://www.apple.com",
        "career_page": "https://jobs.apple.com",
        "description": "Creator of iOS, Mac, custom Apple Silicon (M-series), Swift, Apple Intelligence, and distributed services.",
        "size": "160,000+ employees",
        "founded_year": 1976,
        "is_featured": True
    },
    {
        "id": "netflix",
        "name": "Netflix",
        "logo": "https://assets.nflxext.com/ffe/siteui/common/icons/nficon2016.ico",
        "industry": "Streaming Entertainment & Microservices",
        "headquarters": "Los Gatos, CA, USA",
        "locations": ["Mumbai, India", "Los Gatos, USA", "Amsterdam, Netherlands", "Remote"],
        "website": "https://www.netflix.com",
        "career_page": "https://jobs.netflix.com",
        "description": "Global entertainment streaming platform pioneer known for microservice architecture, Chaos Engineering, and recommendation algorithms.",
        "size": "13,000+ employees",
        "founded_year": 1997,
        "is_featured": True
    },
    {
        "id": "tcs",
        "name": "Tata Consultancy Services (TCS)",
        "logo": "https://www.tcs.com/favicon.ico",
        "industry": "IT Services & Enterprise Consulting",
        "headquarters": "Mumbai, Maharashtra, India",
        "locations": ["Mumbai, India", "Bengaluru, India", "Hyderabad, India", "Pune, India", "Chennai, India", "London, UK", "New York, USA"],
        "website": "https://www.tcs.com",
        "career_page": "https://www.tcs.com/careers",
        "description": "India's largest IT multinational delivering end-to-end cloud transformations, digital consulting, and enterprise software engineering.",
        "size": "600,000+ employees",
        "founded_year": 1968,
        "is_featured": True
    },
    {
        "id": "infosys",
        "name": "Infosys",
        "logo": "https://www.infosys.com/favicon.ico",
        "industry": "IT Consulting & Digital Services",
        "headquarters": "Bengaluru, Karnataka, India",
        "locations": ["Bengaluru, India", "Pune, India", "Hyderabad, India", "Chennai, India", "Dallas, USA", "Frankfurt, Germany"],
        "website": "https://www.infosys.com",
        "career_page": "https://www.infosys.com/careers",
        "description": "Global leader in next-generation digital services, cloud enablement (Infosys Cobalt), AI platforms (Topaz), and IT management.",
        "size": "315,000+ employees",
        "founded_year": 1981,
        "is_featured": True
    },
    {
        "id": "wipro",
        "name": "Wipro",
        "logo": "https://www.wipro.com/favicon.ico",
        "industry": "IT Services & Business Consulting",
        "headquarters": "Bengaluru, Karnataka, India",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Pune, India", "Kolkata, India", "East Brunswick, USA", "London, UK"],
        "website": "https://www.wipro.com",
        "career_page": "https://careers.wipro.com",
        "description": "Pioneering Indian IT and engineering services firm operating across cloud computing, cybersecurity, and digital operations.",
        "size": "240,000+ employees",
        "founded_year": 1945,
        "is_featured": True
    },
    {
        "id": "accenture",
        "name": "Accenture",
        "logo": "https://www.accenture.com/favicon.ico",
        "industry": "Global Management & Technology Consulting",
        "headquarters": "Dublin, Ireland",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Pune, India", "Mumbai, India", "New York, USA", "Dublin, Ireland"],
        "website": "https://www.accenture.com",
        "career_page": "https://www.accenture.com/careers",
        "description": "Fortune Global 500 professional services company providing strategy, digital transformation, cloud architecture, and operations.",
        "size": "730,000+ employees",
        "founded_year": 1989,
        "is_featured": True
    },
    {
        "id": "deloitte",
        "name": "Deloitte",
        "logo": "https://www.deloitte.com/favicon.ico",
        "industry": "Consulting, Audit & Technology Advisory",
        "headquarters": "London, United Kingdom",
        "locations": ["Hyderabad, India", "Bengaluru, India", "Mumbai, India", "Gurgaon, India", "New York, USA", "London, UK"],
        "website": "https://www.deloitte.com",
        "career_page": "https://www.deloitte.com/careers",
        "description": "Big Four professional services firm leading large-scale analytics, AI implementation, cloud modernization, and cyber risk.",
        "size": "450,000+ employees",
        "founded_year": 1845,
        "is_featured": True
    },
    {
        "id": "flipkart",
        "name": "Flipkart",
        "logo": "https://www.flipkart.com/favicon.ico",
        "industry": "E-Commerce & Supply Chain Tech",
        "headquarters": "Bengaluru, Karnataka, India",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Mumbai, India", "Delhi-NCR, India"],
        "website": "https://www.flipkart.com",
        "career_page": "https://www.flipkartcareers.com",
        "description": "India's premier e-commerce ecosystem empowering millions of sellers with high-throughput distributed systems, payments, and logistics.",
        "size": "40,000+ employees",
        "founded_year": 2007,
        "is_featured": True
    },
    {
        "id": "nvidia",
        "name": "NVIDIA",
        "logo": "https://www.nvidia.com/favicon.ico",
        "industry": "Semiconductors & Accelerated AI",
        "headquarters": "Santa Clara, CA, USA",
        "locations": ["Bengaluru, India", "Pune, India", "Hyderabad, India", "Santa Clara, USA", "Cambridge, UK"],
        "website": "https://www.nvidia.com",
        "career_page": "https://www.nvidia.com/careers",
        "description": "World leader in GPU computing, CUDA parallel architectures, deep learning supercomputing, and Omniverse robotics.",
        "size": "29,000+ employees",
        "founded_year": 1993,
        "is_featured": True
    },
    {
        "id": "adobe",
        "name": "Adobe",
        "logo": "https://www.adobe.com/favicon.ico",
        "industry": "Creative Cloud & Digital Marketing",
        "headquarters": "San Jose, CA, USA",
        "locations": ["Noida, India", "Bengaluru, India", "San Jose, USA", "Seattle, USA", "London, UK"],
        "website": "https://www.adobe.com",
        "career_page": "https://www.adobe.com/careers",
        "description": "Innovator behind Creative Cloud (Photoshop, Premiere), Document Cloud (PDF standard), and Firefly generative AI.",
        "size": "30,000+ employees",
        "founded_year": 1982,
        "is_featured": True
    },
    {
        "id": "oracle",
        "name": "Oracle",
        "logo": "https://www.oracle.com/favicon.ico",
        "industry": "Database Systems & Enterprise Cloud",
        "headquarters": "Austin, TX, USA",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Pune, India", "Austin, USA", "Redwood Shores, USA"],
        "website": "https://www.oracle.com",
        "career_page": "https://www.oracle.com/careers",
        "description": "Enterprise database pioneer, Oracle Cloud Infrastructure (OCI), Java platform maintainer, and business applications (ERP).",
        "size": "160,000+ employees",
        "founded_year": 1977,
        "is_featured": True
    },
    {
        "id": "ibm",
        "name": "IBM",
        "logo": "https://www.ibm.com/favicon.ico",
        "industry": "Hybrid Cloud & Quantum Computing",
        "headquarters": "Armonk, NY, USA",
        "locations": ["Bengaluru, India", "Hyderabad, India", "Pune, India", "Armonk, USA", "Zurich, Switzerland"],
        "website": "https://www.ibm.com",
        "career_page": "https://www.ibm.com/careers",
        "description": "Pioneering Red Hat OpenShift hybrid cloud, watsonx enterprise AI models, and commercial quantum computing.",
        "size": "280,000+ employees",
        "founded_year": 1911,
        "is_featured": True
    },
    {
        "id": "cloudflare",
        "name": "Cloudflare",
        "logo": "https://www.cloudflare.com/favicon.ico",
        "industry": "Edge Computing & Cybersecurity",
        "headquarters": "San Francisco, CA, USA",
        "locations": ["San Francisco, USA", "Austin, USA", "London, UK", "Singapore", "Remote"],
        "website": "https://www.cloudflare.com",
        "career_page": "https://www.cloudflare.com/careers",
        "description": "Global cloud network protecting and accelerating internet properties with edge workers, DDoS mitigation, and Zero Trust security.",
        "size": "3,500+ employees",
        "founded_year": 2009,
        "is_featured": True
    },
    {
        "id": "gitlab",
        "name": "GitLab",
        "logo": "https://gitlab.com/favicon.ico",
        "industry": "DevSecOps & Open Source",
        "headquarters": "All-Remote (Global)",
        "locations": ["Remote (Worldwide)", "Remote (India)", "Remote (USA)", "Remote (Europe)"],
        "website": "https://gitlab.com",
        "career_page": "https://about.gitlab.com/jobs",
        "description": "The open-source DevSecOps platform delivered as a single application, pioneer in all-remote asynchronous culture.",
        "size": "2,200+ employees",
        "founded_year": 2011,
        "is_featured": True
    },
    {
        "id": "discord",
        "name": "Discord",
        "logo": "https://discord.com/assets/favicon.ico",
        "industry": "Real-Time Communications & Gaming",
        "headquarters": "San Francisco, CA, USA",
        "locations": ["San Francisco, USA", "Remote (USA)", "Remote (International)"],
        "website": "https://discord.com",
        "career_page": "https://discord.com/careers",
        "description": "Voice, video, and text communication service built on Rust, Elixir, and WebRTC serving hundreds of millions of users.",
        "size": "900+ employees",
        "founded_year": 2015,
        "is_featured": True
    },
    {
        "id": "stripe",
        "name": "Stripe",
        "logo": "https://stripe.com/favicon.ico",
        "industry": "Financial Infrastructure & Payments",
        "headquarters": "San Francisco & Dublin",
        "locations": ["Bengaluru, India", "San Francisco, USA", "Dublin, Ireland", "Singapore", "Remote"],
        "website": "https://stripe.com",
        "career_page": "https://stripe.com/jobs",
        "description": "Financial infrastructure for the internet, powering millions of businesses with developer-first payment APIs and billing.",
        "size": "8,000+ employees",
        "founded_year": 2010,
        "is_featured": True
    },
    {
        "id": "uber",
        "name": "Uber",
        "logo": "https://www.uber.com/favicon.ico",
        "industry": "Mobility & Distributed Logistics",
        "headquarters": "San Francisco, CA, USA",
        "locations": ["Bengaluru, India", "Hyderabad, India", "San Francisco, USA", "Amsterdam, Netherlands"],
        "website": "https://www.uber.com",
        "career_page": "https://www.uber.com/careers",
        "description": "Revolutionizing urban mobility, food delivery (Uber Eats), and freight using massive distributed real-time geospatial systems.",
        "size": "32,000+ employees",
        "founded_year": 2009,
        "is_featured": True
    },
    {
        "id": "atlassian",
        "name": "Atlassian",
        "logo": "https://www.atlassian.com/favicon.ico",
        "industry": "Team Collaboration & Developer Tools",
        "headquarters": "Sydney, Australia",
        "locations": ["Bengaluru, India", "Sydney, Australia", "San Francisco, USA", "Remote"],
        "website": "https://www.atlassian.com",
        "career_page": "https://www.atlassian.com/company/careers",
        "description": "Creator of Jira, Confluence, Bitbucket, and Trello powering agile software development and enterprise collaboration worldwide.",
        "size": "11,000+ employees",
        "founded_year": 2002,
        "is_featured": True
    }
]

# =========================================================================
# CURATED BASELINE JOBS (Covering India & International, All Levels & Tech)
# =========================================================================

CURATED_BASELINE_JOBS = [
    # 1. Google - Senior Full Stack Engineer (Bengaluru, India)
    {
        "id": "job_google_fs_blr",
        "title": "Senior Full Stack Software Engineer - Cloud Platform",
        "company": "Google",
        "company_id": "google",
        "company_logo": "https://www.google.com/favicon.ico",
        "location": "Bengaluru, Karnataka, India",
        "city": "Bengaluru",
        "country": "India",
        "work_mode": "Hybrid",
        "role_category": "Full Stack Developer",
        "experience_level": "Senior",
        "employment_type": "Full-time",
        "salary_min": 3500000,
        "salary_max": 5500000,
        "salary_currency": "INR",
        "salary_text": "₹35,00,000 - ₹55,00,000",
        "skills": ["Go", "Python", "React", "TypeScript", "GCP", "Kubernetes", "gRPC", "Distributed Systems", "SQL"],
        "description": """About the Role:
As a Senior Full Stack Software Engineer on Google Cloud, you will architect developer platforms and analytics consoles used by millions of engineers globally. You will collaborate with product designers, systems infrastructure teams, and site reliability engineers.

Key Responsibilities:
- Design, build, and deploy low-latency web applications using TypeScript, React, and internal Google frontend frameworks.
- Engineer high-throughput backend microservices and gRPC APIs in Go and Python.
- Optimize distributed storage layers and Spanner/PostgreSQL database queries under massive concurrency.
- Champion engineering excellence, code reviews, unit testing, and automated canary deployments.
- Mentor junior and mid-level software engineers across Google's Bengaluru campus.

Minimum Qualifications:
- Bachelor's or Master's degree in Computer Science, Electrical Engineering, or equivalent practical experience.
- 5+ years of full stack software engineering experience with Go, Python, Java, or C++.
- Strong proficiency in modern JavaScript/TypeScript, React, and responsive frontend architecture.
- Deep understanding of distributed systems, concurrency primitives, and microservice patterns.
- Excellent problem-solving skills and communication capabilities in cross-functional teams.""",
        "url": "https://careers.google.com/jobs/results/",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 10, 10, 0, 0)
    },
    # 2. Microsoft - Software Engineer Fresher / Entry Level (Hyderabad, India)
    {
        "id": "job_msft_swe_entry_hyd",
        "title": "Software Engineer (Entry-Level / Fresher) - Azure Core",
        "company": "Microsoft",
        "company_id": "microsoft",
        "company_logo": "https://www.microsoft.com/favicon.ico",
        "location": "Hyderabad, Telangana, India",
        "city": "Hyderabad",
        "country": "India",
        "work_mode": "Hybrid",
        "role_category": "Software Engineer",
        "experience_level": "Fresher / Entry",
        "employment_type": "Full-time",
        "salary_min": 1400000,
        "salary_max": 2000000,
        "salary_currency": "INR",
        "salary_text": "₹14,00,000 - ₹20,00,000",
        "skills": ["C++", "C#", "Python", "Data Structures", "Algorithms", "Azure", "Git", "OOP"],
        "description": """About the Role:
Microsoft IDC Hyderabad is looking for talented entry-level Software Engineers and 2025/2026 fresh graduates to join Azure Core Engineering. You will work on foundational cloud compute, storage, and networking systems.

Responsibilities:
- Write clean, well-tested code in C++, C#, or Python following SOLID object-oriented principles.
- Participate in designing and implementing reliable microservices and internal developer tooling.
- Troubleshoot distributed system logs, performance bottlenecks, and telemetry alerts.
- Work closely with senior mentors and architects in an agile, supportive engineering environment.

Requirements:
- B.Tech / B.E. / M.Tech in Computer Science, IT, or related quantitative field (2025/2026 batch or up to 1 year experience).
- Strong foundations in Data Structures, Algorithms, Complexity Analysis, and Operating Systems.
- Proficiency in at least one modern language: C++, C#, Java, or Python.
- Eagerness to learn cloud-scale computing and automated CI/CD practices.""",
        "url": "https://careers.microsoft.com/professionals/us/en",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 12, 14, 30, 0)
    },
    # 3. Amazon - AI / ML Engineer (Bengaluru, India)
    {
        "id": "job_amazon_aiml_blr",
        "title": "AI / Machine Learning Engineer - Alexa & Generative Search",
        "company": "Amazon",
        "company_id": "amazon",
        "company_logo": "https://www.amazon.com/favicon.ico",
        "location": "Bengaluru, Karnataka, India",
        "city": "Bengaluru",
        "country": "India",
        "work_mode": "On-site",
        "role_category": "AI/ML Engineer",
        "experience_level": "Mid-level",
        "employment_type": "Full-time",
        "salary_min": 2800000,
        "salary_max": 4200000,
        "salary_currency": "INR",
        "salary_text": "₹28,00,000 - ₹42,00,000",
        "skills": ["Python", "PyTorch", "NLP", "LLMs", "RAG", "AWS", "Docker", "Scikit-learn", "FastAPI"],
        "description": """About the Role:
Amazon is seeking an AI/ML Engineer in Bengaluru to design and deploy Large Language Model (LLM) inference systems and retrieval-augmented generation (RAG) pipelines for customer experience workflows.

Responsibilities:
- Develop NLP pipelines and fine-tune open-source Transformer models using PyTorch and Hugging Face.
- Build production-ready RAG architectures integrating vector databases (OpenSearch, Pinecone) with AWS Bedrock.
- Optimize low-latency model inference servers utilizing FastAPI, Docker, and ONNX Runtime.
- Measure model accuracy, hallucinations, and latency regressions through automated evaluation suites.

Requirements:
- 3+ years of professional experience building ML or NLP systems in production.
- Strong hands-on coding proficiency in Python and statistical data manipulation (NumPy, Pandas).
- Practical experience fine-tuning LLMs, implementing prompt engineering, and building vector search systems.
- Familiarity with AWS cloud services (S3, SageMaker, EC2) and containerization.""",
        "url": "https://www.amazon.jobs/",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 11, 9, 15, 0)
    },
    # 4. TCS - Python Full Stack Developer (Pune / Hyderabad, India)
    {
        "id": "job_tcs_py_fullstack",
        "title": "Full Stack Developer (Python & React) - Digital Transformation",
        "company": "Tata Consultancy Services (TCS)",
        "company_id": "tcs",
        "company_logo": "https://www.tcs.com/favicon.ico",
        "location": "Pune, Maharashtra, India",
        "city": "Pune",
        "country": "India",
        "work_mode": "Hybrid",
        "role_category": "Full Stack Developer",
        "experience_level": "Mid-level",
        "employment_type": "Full-time",
        "salary_min": 900000,
        "salary_max": 1500000,
        "salary_currency": "INR",
        "salary_text": "₹9,00,000 - ₹15,00,000",
        "skills": ["Python", "Django", "FastAPI", "React", "JavaScript", "SQL", "PostgreSQL", "Docker", "Git"],
        "description": """About the Opportunity:
TCS is hiring Full Stack Developers with 2 to 5 years of experience to lead enterprise application modernization for global banking and retail clients.

Key Responsibilities:
- Build robust backend microservices using Python (FastAPI / Django) connected to PostgreSQL and Redis.
- Develop interactive, accessible single-page web applications using React, Tailwind CSS, and Redux.
- Implement secure RESTful APIs, JWT authentication, and role-based access control (RBAC).
- Collaborate in agile Scrum sprints, conducting code reviews and maintaining CI/CD pipelines via Git.

Qualifications:
- 2-5 years of hands-on experience in full stack software development.
- Strong knowledge of Python, React, and relational database design.
- Familiarity with containerization (Docker) and REST architecture.""",
        "url": "https://www.tcs.com/careers",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 13, 8, 0, 0)
    },
    # 5. Flipkart - Data Analyst / Business Intelligence (Bengaluru, India)
    {
        "id": "job_flipkart_data_analyst",
        "title": "Data Analyst II - Supply Chain & Customer Intelligence",
        "company": "Flipkart",
        "company_id": "flipkart",
        "company_logo": "https://www.flipkart.com/favicon.ico",
        "location": "Bengaluru, Karnataka, India",
        "city": "Bengaluru",
        "country": "India",
        "work_mode": "On-site",
        "role_category": "Data Analyst",
        "experience_level": "Mid-level",
        "employment_type": "Full-time",
        "salary_min": 1600000,
        "salary_max": 2400000,
        "salary_currency": "INR",
        "salary_text": "₹16,00,000 - ₹24,00,000",
        "skills": ["SQL", "Python", "Tableau", "Power BI", "Data Analytics", "Pandas", "Statistical Analysis"],
        "description": """About Flipkart Supply Chain Analytics:
Flipkart processes millions of daily orders across India. As a Data Analyst II, you will uncover critical logistics insights, delivery efficiency metrics, and customer retention drivers.

Responsibilities:
- Write complex analytical SQL queries, CTEs, and window functions on petabyte-scale data lakes.
- Build executive dashboards in Power BI and Tableau tracking delivery SLAs, fulfillment costs, and return rates.
- Perform exploratory data analysis (EDA) and cohort retention modeling in Python (Pandas, Seaborn).
- Partner with product managers and operational directors to translate data into strategic decisions.

Qualifications:
- 2-4 years of experience as a Data Analyst or BI Engineer.
- Advanced SQL proficiency (BigQuery, PostgreSQL, Hive, or Snowflake).
- Strong data storytelling and visualization skills using Power BI or Tableau.
- Solid Python scripting skills for automating repetitive data transformations.""",
        "url": "https://www.flipkartcareers.com",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 12, 11, 20, 0)
    },
    # 6. Infosys - Cloud & DevOps Engineer (Bengaluru, India)
    {
        "id": "job_infosys_devops_blr",
        "title": "Cloud & DevOps Engineer - Azure / AWS Cobalt",
        "company": "Infosys",
        "company_id": "infosys",
        "company_logo": "https://www.infosys.com/favicon.ico",
        "location": "Bengaluru, Karnataka, India",
        "city": "Bengaluru",
        "country": "India",
        "work_mode": "Hybrid",
        "role_category": "DevOps",
        "experience_level": "Junior",
        "employment_type": "Full-time",
        "salary_min": 800000,
        "salary_max": 1300000,
        "salary_currency": "INR",
        "salary_text": "₹8,00,000 - ₹13,00,000",
        "skills": ["AWS", "Azure", "Docker", "Kubernetes", "CI/CD", "Terraform", "Linux", "Bash", "GitHub Actions"],
        "description": """About the Role:
Infosys Cobalt Cloud Practice is hiring Cloud & DevOps Engineers to design automated deployment pipelines and configure resilient cloud infrastructure for Fortune 500 enterprises.

Responsibilities:
- Build and maintain continuous integration and continuous deployment (CI/CD) pipelines using GitHub Actions and Jenkins.
- Provision infrastructure as code (IaC) utilizing Terraform and AWS CloudFormation.
- Manage Docker containers and Kubernetes clusters across development and staging environments.
- Configure monitoring, alerting, and logging systems using Prometheus, Grafana, and CloudWatch.

Requirements:
- 1-3 years experience in DevOps, Cloud Engineering, or System Administration.
- Solid understanding of Linux CLI, Bash scripting, and Git workflows.
- Hands-on experience with either AWS or Azure and container technologies (Docker).""",
        "url": "https://www.infosys.com/careers",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 11, 16, 45, 0)
    },
    # 7. Stripe - Frontend Software Engineer (San Francisco, USA / Remote)
    {
        "id": "job_stripe_fe_sf",
        "title": "Frontend Software Engineer - Payment Dashboard",
        "company": "Stripe",
        "company_id": "stripe",
        "company_logo": "https://stripe.com/favicon.ico",
        "location": "San Francisco, CA, USA",
        "city": "San Francisco",
        "country": "USA",
        "work_mode": "Remote",
        "role_category": "Frontend Developer",
        "experience_level": "Senior",
        "employment_type": "Full-time",
        "salary_min": 175000,
        "salary_max": 235000,
        "salary_currency": "USD",
        "salary_text": "$175,000 - $235,000 / yr",
        "skills": ["React", "TypeScript", "Next.js", "CSS", "UI/UX", "GraphQL", "Jest", "Web Performance"],
        "description": """About Stripe Frontend:
Stripe builds the financial infrastructure for the internet. Millions of businesses—from ambitious startups to public corporations—rely on Stripe's web interface to manage their revenue.

Responsibilities:
- Build highly polished, performant, and accessible frontend interfaces in React and TypeScript.
- Craft reusable UI design system components ensuring sub-100ms interaction latency.
- Collaborate closely with product managers, designers, and API engineers to simplify complex banking workflows.
- Architect real-time charts and financial dashboards handling millions in transaction telemetry.

Requirements:
- 4+ years of professional frontend web development experience.
- Expert-level TypeScript and React proficiency.
- Strong intuition for user experience, component modularity, and web performance optimization.""",
        "url": "https://stripe.com/jobs",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 10, 15, 0, 0)
    },
    # 8. GitLab - Backend Engineer Intern / Junior (Remote Worldwide)
    {
        "id": "job_gitlab_intern_remote",
        "title": "Backend Engineering Intern / Junior - Core Platform",
        "company": "GitLab",
        "company_id": "gitlab",
        "company_logo": "https://gitlab.com/favicon.ico",
        "location": "Remote (Worldwide)",
        "city": "Remote",
        "country": "Global",
        "work_mode": "Remote",
        "role_category": "Backend Developer",
        "experience_level": "Internship",
        "employment_type": "Internship",
        "salary_min": 50000,
        "salary_max": 75000,
        "salary_currency": "USD",
        "salary_text": "$50,000 - $75,000 (Annualized)",
        "skills": ["Ruby", "Ruby on Rails", "Go", "PostgreSQL", "Git", "REST API", "Docker", "Unit Testing"],
        "description": """About the Internship:
GitLab is the open-source DevSecOps platform delivered as a single application. As a Backend Intern, you will write production code that ships to millions of developers around the world.

Responsibilities:
- Implement features and bug fixes across GitLab's open-source codebase in Ruby on Rails and Go.
- Write unit tests with RSpec and ensure high code coverage.
- Learn asynchronous collaboration, merge request etiquette, and distributed system debugging.
- Participate in weekly architectural mentoring with senior staff engineers.

Qualifications:
- Currently enrolled in or recently graduated from a Computer Science or related university program.
- Good understanding of object-oriented programming, data structures, and relational databases.
- Prior experience with Git and at least one programming language (Ruby, Python, Go, or Java).""",
        "url": "https://about.gitlab.com/jobs",
        "source": "Greenhouse",
        "posted_date": datetime(2026, 11, 13, 9, 30, 0)
    },
    # 9. Cloudflare - Systems & Security Engineer (London, UK / Hybrid)
    {
        "id": "job_cloudflare_sec_lon",
        "title": "Systems & Cybersecurity Engineer - Edge Security",
        "company": "Cloudflare",
        "company_id": "cloudflare",
        "company_logo": "https://www.cloudflare.com/favicon.ico",
        "location": "London, United Kingdom",
        "city": "London",
        "country": "UK",
        "work_mode": "Hybrid",
        "role_category": "Cybersecurity",
        "experience_level": "Senior",
        "employment_type": "Full-time",
        "salary_min": 95000,
        "salary_max": 130000,
        "salary_currency": "GBP",
        "salary_text": "£95,000 - £130,000 / yr",
        "skills": ["Rust", "Go", "Linux", "Networking", "TCP", "UDP", "TLS", "Cybersecurity", "Distributed Systems"],
        "description": """About Cloudflare Security:
Cloudflare handles approximately 20% of all internet traffic. As an Edge Security Engineer in our London office, you will defend global infrastructure against multi-terabit DDoS attacks and zero-day vulnerabilities.

Responsibilities:
- Write lightning-fast, memory-safe edge security filters in Rust and Go.
- Analyze BGP routing anomalies, DNS exploits, and high-volume packet floods in real time.
- Build automated mitigation rules operating at line-rate across Cloudflare's global anycast network.
- Collaborate with threat intelligence teams to publish research on emerging attack vectors.

Requirements:
- 4+ years of systems programming experience in Rust, Go, or C.
- Deep understanding of TCP/IP, UDP, TLS handshakes, and Linux kernel networking.
- Strong passion for internet resilience and cybersecurity.""",
        "url": "https://www.cloudflare.com/careers",
        "source": "Greenhouse",
        "posted_date": datetime(2026, 11, 12, 13, 0, 0)
    },
    # 10. NVIDIA - Deep Learning Research Scientist (Bengaluru / Santa Clara)
    {
        "id": "job_nvidia_dl_blr",
        "title": "Deep Learning Research Scientist - LLM Architectures",
        "company": "NVIDIA",
        "company_id": "nvidia",
        "company_logo": "https://www.nvidia.com/favicon.ico",
        "location": "Bengaluru, Karnataka, India",
        "city": "Bengaluru",
        "country": "India",
        "work_mode": "On-site",
        "role_category": "Data Scientist",
        "experience_level": "Senior",
        "employment_type": "Full-time",
        "salary_min": 4000000,
        "salary_max": 6500000,
        "salary_currency": "INR",
        "salary_text": "₹40,00,000 - ₹65,00,000",
        "skills": ["Python", "PyTorch", "CUDA", "C++", "Deep Learning", "Transformers", "Model Evaluation"],
        "description": """About NVIDIA Research:
NVIDIA pioneered accelerated computing to tackle challenges no one else can solve. Our Deep Learning research team explores frontier transformer architectures, quantization techniques, and multi-GPU training algorithms.

Responsibilities:
- Research novel attention mechanisms, mixture-of-experts (MoE) architectures, and efficient KV caching.
- Optimize distributed training pipelines across clusters of thousands of NVIDIA H100 and Blackwell GPUs.
- Implement CUDA kernels and PyTorch extensions for high-throughput model inference.
- Publish findings at top-tier ML conferences (NeurIPS, ICML, ICLR).

Requirements:
- Ph.D. or Master's in Computer Science, Machine Learning, or related quantitative field.
- Extensive publication or industry record in deep learning, transformer models, or GPU acceleration.
- Deep expertise with PyTorch, Python, and C++/CUDA.""",
        "url": "https://www.nvidia.com/careers",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 11, 11, 0, 0)
    },
    # 11. Accenture - Product Manager - Enterprise AI (Mumbai / Gurgaon, India)
    {
        "id": "job_accenture_pm_ai",
        "title": "Technical Product Manager - Enterprise AI Solutions",
        "company": "Accenture",
        "company_id": "accenture",
        "company_logo": "https://www.accenture.com/favicon.ico",
        "location": "Gurgaon, Haryana, India",
        "city": "Gurgaon",
        "country": "India",
        "work_mode": "Hybrid",
        "role_category": "Product Manager",
        "experience_level": "Senior",
        "employment_type": "Full-time",
        "salary_min": 2400000,
        "salary_max": 3600000,
        "salary_currency": "INR",
        "salary_text": "₹24,00,000 - ₹36,00,000",
        "skills": ["Product Management", "Agile", "Scrum", "AI", "Cloud", "Roadmapping", "System Design", "Leadership"],
        "description": """About the Role:
Accenture is looking for an experienced Technical Product Manager to define and lead the rollout of generative AI and automation platforms for enterprise clients across financial services and healthcare.

Responsibilities:
- Formulate product roadmaps, prioritize feature backlogs, and define user stories in Jira.
- Bridge client executive stakeholders with software engineering and data science teams.
- Define quantitative success metrics (KPIs), track adoption rates, and run client user-research sessions.
- Ensure strict compliance with data privacy standards and enterprise security protocols.

Qualifications:
- 5+ years of product management experience delivering enterprise software or data/AI products.
- Strong technical background with ability to evaluate architectural trade-offs with senior engineers.
- Proven experience with agile methodologies, roadmap synthesis, and cross-functional leadership.""",
        "url": "https://www.accenture.com/careers",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 12, 16, 0, 0)
    },
    # 12. Atlassian - Cloud Infrastructure Engineer (Bengaluru, India / Remote)
    {
        "id": "job_atlassian_cloud_infra",
        "title": "Cloud Infrastructure Engineer - Jira Cloud Platform",
        "company": "Atlassian",
        "company_id": "atlassian",
        "company_logo": "https://www.atlassian.com/favicon.ico",
        "location": "Bengaluru, Karnataka, India",
        "city": "Bengaluru",
        "country": "India",
        "work_mode": "Remote",
        "role_category": "Cloud Engineer",
        "experience_level": "Mid-level",
        "employment_type": "Full-time",
        "salary_min": 2600000,
        "salary_max": 3800000,
        "salary_currency": "INR",
        "salary_text": "₹26,00,000 - ₹38,00,000",
        "skills": ["AWS", "Terraform", "Kubernetes", "Python", "Docker", "Linux", "Datadog", "CI/CD"],
        "description": """About the Team:
Atlassian's Cloud Platform team ensures that Jira and Confluence remain highly available, resilient, and fast for over 250,000 global customers.

Responsibilities:
- Build and maintain multi-region AWS cloud infrastructure using Terraform and internal orchestrators.
- Optimize Kubernetes cluster autoscaling, network ingress, and service mesh connectivity.
- Develop operational automation in Python and Go to eliminate toil and streamline deployments.
- Participate in on-call rotations, blameless post-incident reviews, and SLO monitoring.

Requirements:
- 3+ years experience managing production cloud infrastructure (AWS preferred).
- Strong proficiency with Terraform, Kubernetes, and containerized microservice architectures.
- Scripting proficiency in Python or Go, with a solid grasp of Linux networking and observability.""",
        "url": "https://www.atlassian.com/company/careers",
        "source": "Official Careers",
        "posted_date": datetime(2026, 11, 13, 10, 15, 0)
    }
]

# =========================================================================
# JOB AGGREGATOR SERVICE
# =========================================================================

class JobAggregatorService:
    """
    Orchestrates job listings across:
    1. Real public APIs (Remotive, Arbeitnow, Greenhouse public boards).
    2. Curated enterprise baseline database (India & International).
    3. Dynamic search, filtering, deduplication, and persistence in SQLite.
    """

    def __init__(self):
        self.last_sync_time: Optional[datetime] = None

    def ensure_seed_data(self, db: Session):
        """Seed initial companies and curated jobs if database tables are empty."""
        company_count = db.query(CompanyProfile).count()
        if company_count == 0:
            print("[INFO] Seeding initial company profiles...")
            for comp in INITIAL_COMPANIES:
                company_obj = CompanyProfile(
                    id=comp["id"],
                    name=comp["name"],
                    logo=comp["logo"],
                    industry=comp["industry"],
                    headquarters=comp["headquarters"],
                    locations=json.dumps(comp["locations"]),
                    website=comp["website"],
                    career_page=comp["career_page"],
                    description=comp["description"],
                    size=comp["size"],
                    founded_year=comp.get("founded_year"),
                    is_featured=comp.get("is_featured", False),
                    openings_count=0
                )
                db.add(company_obj)
            db.commit()

        job_count = db.query(JobListing).count()
        if job_count == 0:
            print("[INFO] Seeding baseline job records...")
            for j in CURATED_BASELINE_JOBS:
                job_obj = JobListing(
                    id=j["id"],
                    title=j["title"],
                    company=j["company"],
                    company_id=j.get("company_id", ""),
                    company_logo=j.get("company_logo", ""),
                    location=j["location"],
                    city=j.get("city", ""),
                    country=j.get("country", "Global"),
                    work_mode=j.get("work_mode", "Remote"),
                    role_category=j.get("role_category", "Software Engineering"),
                    experience_level=j.get("experience_level", "Mid-level"),
                    employment_type=j.get("employment_type", "Full-time"),
                    salary_min=j.get("salary_min"),
                    salary_max=j.get("salary_max"),
                    salary_currency=j.get("salary_currency", "USD"),
                    salary_text=j.get("salary_text", ""),
                    skills=json.dumps(j.get("skills", [])),
                    description=j["description"],
                    url=j["url"],
                    source=j.get("source", "Official Careers"),
                    posted_date=j.get("posted_date", datetime.utcnow()),
                    is_active=True
                )
                db.add(job_obj)
            db.commit()

        # Update company openings count
        self.recalculate_company_openings(db)

    def recalculate_company_openings(self, db: Session):
        """Update openings_count for all companies based on active jobs in database."""
        companies = db.query(CompanyProfile).all()
        for c in companies:
            count = db.query(JobListing).filter(
                JobListing.is_active == True,
                or_(
                    JobListing.company_id == c.id,
                    JobListing.company.ilike(f"%{c.name}%")
                )
            ).count()
            c.openings_count = count
        db.commit()

    # =========================================================================
    # LIVE EXTERNAL APIS FETCHERS
    # =========================================================================

    def fetch_live_remotive_jobs(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetch live remote developer jobs from Remotive public API."""
        url = f"https://remotive.com/api/remote-jobs?limit={limit}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read().decode("utf-8"))
                jobs = data.get("jobs", [])
                normalized = []
                for item in jobs:
                    title = item.get("title", "Software Engineer")
                    company = item.get("company_name", "Remote Tech Company")
                    desc_html = item.get("description", "")
                    # Clean simple HTML tags for text
                    desc_clean = re.sub(r"<[^>]+>", " ", desc_html).strip()
                    desc_clean = re.sub(r"\s+", " ", desc_clean)
                    
                    category = self._categorize_role(title, item.get("category", ""))
                    exp_level = self._detect_experience_level(title, desc_clean)
                    
                    skills = item.get("tags", [])
                    if not skills:
                        skills = extract_skills_from_text(desc_clean)[:8]
                    
                    salary_text = item.get("salary", "")
                    
                    normalized.append({
                        "id": f"remotive_{item.get('id', hash(title + company))}",
                        "title": title,
                        "company": company,
                        "company_id": self._slugify(company),
                        "company_logo": item.get("company_logo", ""),
                        "location": item.get("candidate_required_location", "Remote Worldwide"),
                        "city": "Remote",
                        "country": "Global",
                        "work_mode": "Remote",
                        "role_category": category,
                        "experience_level": exp_level,
                        "employment_type": "Full-time" if item.get("job_type") == "full_time" else "Contract",
                        "salary_text": salary_text,
                        "skills": skills[:8],
                        "description": desc_clean,
                        "url": item.get("url", ""),
                        "source": "Remotive",
                        "posted_date": datetime.utcnow()
                    })
                return normalized
        except Exception as e:
            print(f"[WARN] Failed to fetch Remotive live jobs: {e}")
            return []

    def fetch_live_arbeitnow_jobs(self) -> List[Dict[str, Any]]:
        """Fetch live tech jobs from Arbeitnow public API."""
        url = "https://www.arbeitnow.com/api/job-board-api"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read().decode("utf-8"))
                jobs = data.get("data", [])
                normalized = []
                for item in jobs[:30]:  # limit to top 30 fresh items
                    title = item.get("title", "Developer")
                    company = item.get("company_name", "Technology Employer")
                    desc_html = item.get("description", "")
                    desc_clean = re.sub(r"<[^>]+>", " ", desc_html).strip()
                    desc_clean = re.sub(r"\s+", " ", desc_clean)
                    
                    is_remote = item.get("remote", False)
                    location = item.get("location", "Remote" if is_remote else "Global")
                    
                    category = self._categorize_role(title, "")
                    exp_level = self._detect_experience_level(title, desc_clean)
                    
                    tags = item.get("tags", [])
                    extracted_skills = tags if tags else extract_skills_from_text(desc_clean)[:8]
                    
                    normalized.append({
                        "id": f"arbeitnow_{item.get('slug', hash(title + company))}",
                        "title": title,
                        "company": company,
                        "company_id": self._slugify(company),
                        "company_logo": "",
                        "location": location,
                        "city": location.split(",")[0].strip() if "," in location else location,
                        "country": "Germany" if "germany" in location.lower() or "berlin" in location.lower() else "Europe",
                        "work_mode": "Remote" if is_remote else "Hybrid",
                        "role_category": category,
                        "experience_level": exp_level,
                        "employment_type": "Full-time",
                        "salary_text": "",
                        "skills": extracted_skills[:8],
                        "description": desc_clean,
                        "url": item.get("url", ""),
                        "source": "Arbeitnow",
                        "posted_date": datetime.utcnow()
                    })
                return normalized
        except Exception as e:
            print(f"[WARN] Failed to fetch Arbeitnow live jobs: {e}")
            return []

    def fetch_live_greenhouse_board(self, company_token: str, company_name: str) -> List[Dict[str, Any]]:
        """Fetch live postings from official Greenhouse career board."""
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_token}/jobs?content=true"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read().decode("utf-8"))
                jobs = data.get("jobs", [])
                normalized = []
                for item in jobs[:20]:  # limit to 20 per board
                    title = item.get("title", "Software Engineer")
                    loc_name = item.get("location", {}).get("name", "Remote")
                    desc_html = item.get("content", "")
                    desc_clean = re.sub(r"<[^>]+>", " ", desc_html).strip()
                    desc_clean = re.sub(r"\s+", " ", desc_clean)
                    
                    category = self._categorize_role(title, "")
                    exp_level = self._detect_experience_level(title, desc_clean)
                    skills = extract_skills_from_text(desc_clean)[:8]
                    
                    normalized.append({
                        "id": f"gh_{company_token}_{item.get('id', hash(title))}",
                        "title": title,
                        "company": company_name,
                        "company_id": company_token,
                        "company_logo": f"https://www.{company_token}.com/favicon.ico",
                        "location": loc_name,
                        "city": loc_name.split(",")[0].strip() if "," in loc_name else loc_name,
                        "country": "India" if "india" in loc_name.lower() or "bengaluru" in loc_name.lower() else ("USA" if "usa" in loc_name.lower() or "united states" in loc_name.lower() else "Global"),
                        "work_mode": "Remote" if "remote" in loc_name.lower() else "Hybrid",
                        "role_category": category,
                        "experience_level": exp_level,
                        "employment_type": "Full-time",
                        "salary_text": "",
                        "skills": skills,
                        "description": desc_clean if len(desc_clean) > 50 else f"Role: {title} at {company_name}. Apply directly on the official career board.",
                        "url": item.get("absolute_url", f"https://boards.greenhouse.io/{company_token}"),
                        "source": "Greenhouse",
                        "posted_date": datetime.utcnow()
                    })
                return normalized
        except Exception as e:
            print(f"[WARN] Failed to fetch Greenhouse board for {company_token}: {e}")
            return []

    def sync_live_jobs(self, db: Session) -> Dict[str, Any]:
        """
        Orchestrates syncing live listings from Remotive, Arbeitnow, and Greenhouse boards.
        Deduplicates against SQLite and returns sync metrics.
        """
        fetched_jobs: List[Dict[str, Any]] = []

        # 1. Remotive API
        remotive_jobs = self.fetch_live_remotive_jobs(limit=25)
        fetched_jobs.extend(remotive_jobs)

        # 2. Arbeitnow API
        arbeitnow_jobs = self.fetch_live_arbeitnow_jobs()
        fetched_jobs.extend(arbeitnow_jobs)

        # 3. Greenhouse Boards for top tech
        gh_cloudflare = self.fetch_live_greenhouse_board("cloudflare", "Cloudflare")
        fetched_jobs.extend(gh_cloudflare)

        gh_gitlab = self.fetch_live_greenhouse_board("gitlab", "GitLab")
        fetched_jobs.extend(gh_gitlab)

        gh_discord = self.fetch_live_greenhouse_board("discord", "Discord")
        fetched_jobs.extend(gh_discord)

        added_count = 0
        for j in fetched_jobs:
            existing = db.query(JobListing).filter(JobListing.id == j["id"]).first()
            if not existing:
                # Also ensure no duplicate title + company combo
                dup = db.query(JobListing).filter(
                    JobListing.title == j["title"],
                    JobListing.company == j["company"]
                ).first()
                if not dup:
                    job_obj = JobListing(
                        id=j["id"],
                        title=j["title"],
                        company=j["company"],
                        company_id=j.get("company_id", ""),
                        company_logo=j.get("company_logo", ""),
                        location=j["location"],
                        city=j.get("city", ""),
                        country=j.get("country", "Global"),
                        work_mode=j.get("work_mode", "Remote"),
                        role_category=j.get("role_category", "Software Engineering"),
                        experience_level=j.get("experience_level", "Mid-level"),
                        employment_type=j.get("employment_type", "Full-time"),
                        salary_text=j.get("salary_text", ""),
                        skills=json.dumps(j.get("skills", [])),
                        description=j["description"],
                        url=j["url"],
                        source=j.get("source", "Live API"),
                        posted_date=j.get("posted_date", datetime.utcnow()),
                        is_active=True
                    )
                    db.add(job_obj)
                    added_count += 1

        db.commit()
        self.last_sync_time = datetime.now(timezone.utc)
        self.recalculate_company_openings(db)

        total_active = db.query(JobListing).filter(JobListing.is_active == True).count()
        return {
            "status": "success",
            "message": f"Successfully synchronized live job feeds. Fetched {len(fetched_jobs)} total listings, added {added_count} new unique jobs.",
            "fetched": len(fetched_jobs),
            "added": added_count,
            "total_active_jobs": total_active
        }

    # =========================================================================
    # QUERY & FILTER ENGINE
    # =========================================================================

    def search_jobs(
        self,
        db: Session,
        search: Optional[str] = None,
        role: Optional[str] = None,
        company: Optional[str] = None,
        location: Optional[str] = None,
        country: Optional[str] = None,
        work_mode: Optional[str] = None,
        experience_level: Optional[str] = None,
        skills: Optional[str] = None,
        job_type: Optional[str] = None,
        salary_min: Optional[float] = None,
        page: int = 1,
        limit: int = 12,
        sort_by: str = "recent"
    ) -> Tuple[List[JobListing], int, int]:
        """
        Executes multi-parameter filtering across all active job postings.
        Returns: (jobs_page, total_count, total_pages)
        """
        query = db.query(JobListing).filter(JobListing.is_active == True)

        # 1. Global keyword search (Title, Company, Description, Skills)
        if search and search.strip():
            terms = search.strip().split()
            for t in terms:
                term_pat = f"%{t}%"
                query = query.filter(
                    or_(
                        JobListing.title.ilike(term_pat),
                        JobListing.company.ilike(term_pat),
                        JobListing.location.ilike(term_pat),
                        JobListing.skills.ilike(term_pat),
                        JobListing.description.ilike(term_pat)
                    )
                )

        # 2. Role Category
        if role and role.strip() and role.lower() != "all":
            query = query.filter(JobListing.role_category.ilike(f"%{role.strip()}%"))

        # 3. Company
        if company and company.strip() and company.lower() != "all":
            query = query.filter(
                or_(
                    JobListing.company.ilike(f"%{company.strip()}%"),
                    JobListing.company_id == company.strip().lower()
                )
            )

        # 4. Location / City
        if location and location.strip() and location.lower() != "all":
            query = query.filter(JobListing.location.ilike(f"%{location.strip()}%"))

        # 5. Country
        if country and country.strip() and country.lower() != "all":
            query = query.filter(
                or_(
                    JobListing.country.ilike(f"%{country.strip()}%"),
                    JobListing.location.ilike(f"%{country.strip()}%")
                )
            )

        # 6. Work Mode (Remote, Hybrid, On-site)
        if work_mode and work_mode.strip() and work_mode.lower() != "all":
            query = query.filter(JobListing.work_mode.ilike(f"%{work_mode.strip()}%"))

        # 7. Experience Level
        if experience_level and experience_level.strip() and experience_level.lower() != "all":
            query = query.filter(JobListing.experience_level.ilike(f"%{experience_level.strip()}%"))

        # 8. Employment Type (Full-time, Internship, Contract)
        if job_type and job_type.strip() and job_type.lower() != "all":
            query = query.filter(JobListing.employment_type.ilike(f"%{job_type.strip()}%"))

        # 9. Required Skills
        if skills and skills.strip():
            skill_list = [s.strip() for s in skills.split(",") if s.strip()]
            for sk in skill_list:
                query = query.filter(JobListing.skills.ilike(f"%{sk}%"))

        # 10. Salary Min
        if salary_min and salary_min > 0:
            query = query.filter(
                or_(
                    JobListing.salary_max >= salary_min,
                    JobListing.salary_min >= salary_min
                )
            )

        # Sorting
        if sort_by == "salary":
            query = query.order_by(desc(JobListing.salary_max), desc(JobListing.posted_date))
        else:  # "recent" default
            query = query.order_by(desc(JobListing.posted_date), desc(JobListing.id))

        total_count = query.count()
        total_pages = max(1, (total_count + limit - 1) // limit)
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()

        return items, total_count, total_pages

    def get_filter_options(self, db: Session) -> Dict[str, List[str]]:
        """Returns distinct filter choices for UI dropdowns."""
        roles = [
            "Software Engineer",
            "Full Stack Developer",
            "Frontend Developer",
            "Backend Developer",
            "AI/ML Engineer",
            "Data Scientist",
            "Data Analyst",
            "DevOps",
            "Cloud Engineer",
            "Cybersecurity",
            "Product Manager",
            "Business Analyst"
        ]

        # Top companies
        top_companies = [c[0] for c in db.query(JobListing.company).distinct().order_by(JobListing.company).all() if c[0]]

        # Locations & hubs
        locations = [
            "Bengaluru, Karnataka, India",
            "Hyderabad, Telangana, India",
            "Pune, Maharashtra, India",
            "Mumbai, Maharashtra, India",
            "Delhi-NCR / Gurgaon, India",
            "Remote Worldwide",
            "San Francisco, CA, USA",
            "London, United Kingdom",
            "Berlin, Germany",
            "Remote (India)",
            "Remote (USA)"
        ]

        exp_levels = ["Internship", "Fresher / Entry", "Junior", "Mid-level", "Senior", "Lead / Principal"]
        work_modes = ["All", "Remote", "Hybrid", "On-site"]
        job_types = ["Full-time", "Internship", "Contract", "Part-time"]

        popular_skills = [
            "Python", "React", "TypeScript", "JavaScript", "AWS", "Docker", "Kubernetes",
            "Go", "Java", "C++", "FastAPI", "Node.js", "SQL", "PostgreSQL", "PyTorch",
            "Data Analytics", "System Design", "CI/CD", "NLP", "LLMs"
        ]

        return {
            "roles": roles,
            "companies": top_companies[:30],
            "locations": locations,
            "experience_levels": exp_levels,
            "work_modes": work_modes,
            "employment_types": job_types,
            "popular_skills": popular_skills
        }

    # =========================================================================
    # HELPER PARSERS
    # =========================================================================

    def _categorize_role(self, title: str, category_hint: str) -> str:
        tl = (title + " " + category_hint).lower()
        if "data analyst" in tl or "business intelligence" in tl or "bi analyst" in tl:
            return "Data Analyst"
        if "machine learning" in tl or "ai engineer" in tl or "nlp" in tl or "computer vision" in tl:
            return "AI/ML Engineer"
        if "data scientist" in tl or "data science" in tl:
            return "Data Scientist"
        if "full stack" in tl or "fullstack" in tl:
            return "Full Stack Developer"
        if "frontend" in tl or "front-end" in tl or "react" in tl or "ui engineer" in tl:
            return "Frontend Developer"
        if "backend" in tl or "back-end" in tl or "api engineer" in tl:
            return "Backend Developer"
        if "devops" in tl or "sre" in tl or "site reliability" in tl or "platform engineer" in tl:
            return "DevOps"
        if "cloud" in tl or "aws" in tl or "azure architect" in tl:
            return "Cloud Engineer"
        if "security" in tl or "cyber" in tl or "infosec" in tl:
            return "Cybersecurity"
        if "product manager" in tl or "technical product manager" in tl or "pm" in tl:
            return "Product Manager"
        if "business analyst" in tl:
            return "Business Analyst"
        return "Software Engineer"

    def _detect_experience_level(self, title: str, desc: str) -> str:
        tl = title.lower()
        dl = desc.lower()[:500]
        if "intern" in tl or "internship" in tl:
            return "Internship"
        if "lead" in tl or "principal" in tl or "architect" in tl or "staff" in tl or "director" in tl:
            return "Lead / Principal"
        if "senior" in tl or "sr." in tl or "sr " in tl or "lead" in tl:
            return "Senior"
        if "entry" in tl or "junior" in tl or "jr." in tl or "jr " in tl or "fresher" in tl or "graduate" in tl:
            return "Fresher / Entry"
        if "0-1 year" in dl or "0-2 year" in dl or "freshers" in dl:
            return "Fresher / Entry"
        if "5+ years" in dl or "6+ years" in dl or "7+ years" in dl:
            return "Senior"
        return "Mid-level"

    def _slugify(self, text: str) -> str:
        s = text.lower().strip()
        s = re.sub(r"[^a-z0-9\s-]", "", s)
        return re.sub(r"[\s-]+", "-", s)


# Singleton instance
job_aggregator = JobAggregatorService()
