"""
Curated realistic Job Descriptions and Resume Profiles for instant testing and demonstration.
"""

SAMPLE_JOBS = [
    {
        "id": "fullstack-sr",
        "title": "Senior Full Stack Engineer",
        "company": "Nexus Technologies",
        "department": "Engineering",
        "experience_level": "Senior (4-7 years)",
        "description": """About the Role:
Nexus Technologies is seeking a Senior Full Stack Engineer to lead the architecture and scaling of our enterprise SaaS workflow engine. You will design resilient backend microservices, intuitive modern frontends, and collaborate closely with product management and cloud infrastructure teams.

Responsibilities:
- Architect and develop scalable web applications using React, TypeScript, and modern state management (Redux/Zustand).
- Build high-throughput RESTful APIs and asynchronous background task workers using Python (FastAPI/Django) and Node.js.
- Optimize database schemas and queries in PostgreSQL and manage in-memory caching with Redis.
- Containerize services with Docker and participate in deployment orchestration using Kubernetes and AWS (ECS, S3, RDS).
- Write comprehensive automated tests with Pytest and Jest, achieving over 80% code coverage.
- Champion engineering best practices, CI/CD pipelines via GitHub Actions, and conduct rigorous code reviews.
- Mentor junior and mid-level engineers, fostering an agile culture of continuous improvement.

Requirements & Qualifications:
- 4+ years of professional full stack software development experience.
- Strong proficiency in Python, JavaScript, and TypeScript.
- Deep hands-on experience with React, Tailwind CSS, Node.js, and FastAPI.
- Solid understanding of relational databases (PostgreSQL) and caching strategies (Redis).
- Proven track record with Cloud & DevOps tools: Docker, Kubernetes, AWS, and CI/CD pipelines.
- Experience with System Design, Microservices, and Event-Driven Architecture.
- Excellent communication, cross-functional collaboration, and problem-solving skills.""",
        "key_skills": ["React", "TypeScript", "Python", "FastAPI", "Node.js", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS", "CI/CD", "Tailwind CSS", "System Design"]
    },
    {
        "id": "ai-ml-engineer",
        "title": "AI / Machine Learning Engineer",
        "company": "CognitiveAI Labs",
        "department": "Applied AI",
        "experience_level": "Mid-Senior (3-6 years)",
        "description": """About the Role:
We are looking for an AI/ML Engineer to build and deploy state-of-the-art NLP and Large Language Model applications. You will be responsible for end-to-end model training, fine-tuning, RAG pipeline construction, and production model serving.

Key Responsibilities:
- Design and deploy machine learning models and NLP pipelines using Python, PyTorch, Scikit-learn, and Hugging Face Transformers.
- Build production-grade Retrieval-Augmented Generation (RAG) architectures with LangChain, LlamaIndex, and Vector Databases (Pinecone, ChromaDB).
- Implement efficient semantic search, TF-IDF vectorization, and cosine similarity matching engines.
- Expose low-latency inference endpoints using FastAPI, Docker, and ONNX Runtime.
- Perform feature engineering, statistical evaluation, and data validation using Pandas and NumPy.
- Monitor model performance, latency, and drift in production environments.

Requirements:
- BS/MS in Computer Science, Data Science, or related quantitative field.
- 3+ years hands-on experience building ML/NLP solutions.
- Strong proficiency with Python, Scikit-learn, PyTorch, Pandas, and NumPy.
- Direct experience with LLMs, Prompt Engineering, Vector Databases, and NLP.
- Experience containerizing ML microservices with Docker and deploying to AWS or GCP.
- Familiarity with CI/CD, Git, and REST API development.""",
        "key_skills": ["Python", "Machine Learning", "NLP", "PyTorch", "Scikit-learn", "LLMs", "RAG", "LangChain", "FastAPI", "Docker", "Pandas", "NumPy", "Vector Database"]
    },
    {
        "id": "devops-architect",
        "title": "DevOps & Cloud Architect",
        "company": "CloudStream Systems",
        "department": "Infrastructure",
        "experience_level": "Lead / Principal (5+ years)",
        "description": """About the Role:
CloudStream Systems is seeking a talented DevOps & Cloud Architect to oversee our multi-region AWS cloud infrastructure, Kubernetes clusters, and automated continuous delivery pipelines.

Responsibilities:
- Design, provision, and maintain resilient cloud infrastructure using Terraform and AWS CloudFormation.
- Manage production Kubernetes (EKS) clusters, Helm charts, and service meshes.
- Build and optimize CI/CD pipelines using GitHub Actions and GitLab CI, ensuring secure, zero-downtime deployments.
- Implement comprehensive observability, logging, and alerting systems using Prometheus, Grafana, and Datadog.
- Secure infrastructure following principle of least privilege, IAM policies, and automated vulnerability scanning.
- Automate configuration management and routine operations using Python, Bash, and Ansible.

Qualifications:
- 5+ years experience in DevOps, Cloud Engineering, or Site Reliability Engineering (SRE).
- Extensive expertise with AWS (EC2, S3, RDS, EKS, IAM, VPC).
- Deep knowledge of Docker, Kubernetes, Terraform, and Linux administration.
- Strong background in continuous integration/continuous deployment (CI/CD) tooling.
- Solid scripting skills in Python and Bash.
- Strong problem-solving mindset and incident management experience.""",
        "key_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "GitHub Actions", "Linux", "Prometheus", "Grafana", "Python", "Bash", "Ansible"]
    }
]

SAMPLE_RESUME_TEXT = """ALEX RIVERA
Full Stack & Cloud Software Engineer
San Francisco, CA | (415) 555-0192 | alex.rivera@example.com
github.com/alexrivera | linkedin.com/in/alexrivera-dev | alexrivera.io

SUMMARY
Results-driven Senior Full Stack Engineer with 5+ years of experience designing scalable web applications, distributed APIs, and cloud services. Proven track record of improving system performance by 40%, architecting microservices handling 2M+ daily requests, and leading cross-functional engineering teams.

CORE COMPETENCIES & TECHNICAL SKILLS
- Languages: Python, JavaScript, TypeScript, SQL, Bash
- Frontend: React, Next.js, Redux, Tailwind CSS, HTML5, CSS3, Vite
- Backend & APIs: FastAPI, Node.js, Express, REST API, GraphQL, Microservices
- Databases & Storage: PostgreSQL, Redis, MongoDB, SQLAlchemy
- Cloud & DevOps: Docker, Kubernetes, AWS (S3, EC2, RDS, Lambda), CI/CD, GitHub Actions, Linux
- Practices & Tools: System Design, Git, Agile, Scrum, Unit Testing, Pytest, Jest

PROFESSIONAL EXPERIENCE

Senior Full Stack Engineer | Apex Cloud Solutions, San Francisco, CA
June 2022 – Present
- Architected and deployed a multi-tenant enterprise dashboard using React, TypeScript, Tailwind CSS, and FastAPI, serving 150,000 active users.
- Redesigned backend PostgreSQL database schema and introduced Redis caching layer, reducing API endpoint latency by 45% and query execution time by 60%.
- Engineered automated CI/CD deployment pipelines using Docker and GitHub Actions, cutting production release cycles from 3 hours to 18 minutes.
- Spearheaded migration of legacy monolithic services into containerized microservices orchestrated on AWS ECS and Kubernetes.
- Mentored a cohort of 5 junior and mid-level software engineers through structured pair programming and weekly architectural code reviews.

Software Engineer | Horizon Tech Labs, Austin, TX
August 2020 – May 2022
- Developed responsive web applications using React, Redux, and Node.js/Express, increasing user retention by 28%.
- Integrated RESTful APIs and secure OAuth 2.0 authentication for fintech payment processing services.
- Automated end-to-end testing suites using Jest and Pytest, boosting code test coverage from 52% to 88%.
- Collaborated closely with UI/UX designers and product owners in bi-weekly agile Scrum sprints.

KEY TECHNICAL PROJECTS

CareerSetu – AI Career Intelligence Platform (Personal Project)
- Built a full-stack career platform utilizing React, Tailwind CSS, FastAPI, and Scikit-learn.
- Implemented real NLP algorithms including TF-IDF vectorization and cosine similarity scoring for resume-to-job matching.
- Integrated PyMuPDF for automated PDF resume parsing, section extraction, and skill gap visualization.

CloudScale – Distributed Metrics Monitoring Tool (Open Source)
- Created a lightweight telemetry collector in Python and Node.js supporting real-time streaming via WebSockets and Redis.
- Attracted 600+ GitHub stars and over 50 community contributors.

EDUCATION & CERTIFICATIONS
- Bachelor of Science in Computer Science | University of California, Berkeley (2016 – 2020)
- AWS Certified Solutions Architect – Associate (2023)
"""
