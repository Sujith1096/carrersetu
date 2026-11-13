"""
Comprehensive Skill Bank & Taxonomy for CareerSetu
Contains categorized technical and professional skills with canonical names and synonyms.
"""

SKILL_TAXONOMY = {
    "Programming Languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "SQL", "Bash",
        "Shell", "PowerShell", "Dart", "HTML5", "CSS3", "Solidity", "Perl"
    ],
    "Frontend Development": [
        "React", "React.js", "Next.js", "Vue", "Vue.js", "Nuxt.js", "Angular",
        "Svelte", "SvelteKit", "Tailwind CSS", "TailwindCSS", "Bootstrap", "Sass", "SCSS",
        "Redux", "Redux Toolkit", "Zustand", "MobX", "HTML", "CSS", "Webpack",
        "Vite", "Responsive Design", "UI/UX", "Figma", "Shadcn UI", "Material-UI",
        "Chakra UI", "Storybook", "WebSockets", "PWA"
    ],
    "Backend & APIs": [
        "Node.js", "Express", "Express.js", "FastAPI", "Django", "Flask",
        "Spring Boot", "Ruby on Rails", "ASP.NET Core", "NestJS", "GraphQL",
        "REST API", "RESTful APIs", "gRPC", "Microservices", "Celery", "Kafka",
        "RabbitMQ", "Apache Kafka", "Serverless", "Event-Driven Architecture",
        "JSON", "JWT", "OAuth", "API Gateway"
    ],
    "Databases & Storage": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Cassandra",
        "DynamoDB", "Elasticsearch", "Neo4j", "Snowflake", "BigQuery",
        "Supabase", "Firebase", "Oracle", "MariaDB", "Prisma", "TypeORM",
        "SQLAlchemy", "Mongoose", "Vector Database", "ChromaDB", "Pinecone", "Milvus"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP",
        "Google Cloud Platform", "Docker", "Kubernetes", "K8s", "Terraform",
        "CI/CD", "GitHub Actions", "GitLab CI", "Jenkins", "Linux", "Ubuntu",
        "Nginx", "Apache", "Ansible", "CloudFormation", "Helm", "Prometheus",
        "Grafana", "Datadog", "AWS Lambda", "S3", "EC2", "ECS", "EKS", "IAM"
    ],
    "AI, ML & Data Science": [
        "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
        "Computer Vision", "PyTorch", "TensorFlow", "Scikit-learn", "Pandas",
        "NumPy", "Keras", "Hugging Face", "LLM", "LLMs", "Large Language Models",
        "RAG", "LangChain", "LlamaIndex", "TF-IDF", "Cosine Similarity", "BERT",
        "Transformers", "OpenCV", "Data Visualization", "Power BI", "Tableau",
        "Apache Spark", "Data Analytics", "Feature Engineering", "Model Evaluation",
        "Prompt Engineering", "Fine-tuning", "Vector Embeddings", "Statistical Analysis"
    ],
    "Testing & Quality": [
        "Jest", "Cypress", "Pytest", "Selenium", "Playwright", "Unit Testing",
        "Integration Testing", "E2E Testing", "TDD", "Test-Driven Development",
        "Mocha", "Chai", "Postman", "Swagger", "JMeter", "SonarQube"
    ],
    "Tools & Methodologies": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Agile",
        "Scrum", "Kanban", "System Design", "Distributed Systems", "OOP",
        "Design Patterns", "Clean Code", "Clean Architecture", "Code Review",
        "DevOps", "Version Control", "Continuous Integration"
    ],
    "Soft Skills & Leadership": [
        "Leadership", "Team Leadership", "Cross-Functional Collaboration",
        "Problem Solving", "Communication", "Critical Thinking", "Project Management",
        "Mentorship", "Stakeholder Management", "Strategic Planning", "Adaptability",
        "Time Management", "Analytical Thinking", "Agile Coaching"
    ]
}

# Canonical mapping for normalizing skill variations
CANONICAL_SKILL_MAP = {
    "react.js": "React",
    "reactjs": "React",
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "vue": "Vue",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "express.js": "Express",
    "expressjs": "Express",
    "express": "Express",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "golang": "Go",
    "go": "Go",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "amazon web services": "AWS",
    "aws": "AWS",
    "google cloud platform": "GCP",
    "gcp": "GCP",
    "google cloud": "GCP",
    "microsoft azure": "Azure",
    "azure": "Azure",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "restful apis": "REST API",
    "rest api": "REST API",
    "restful api": "REST API",
    "rest": "REST API",
    "github actions": "GitHub Actions",
    "ci/cd": "CI/CD",
    "continuous integration": "CI/CD",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "large language models": "LLMs",
    "llm": "LLMs",
    "llms": "LLMs",
    "scikit learn": "Scikit-learn",
    "scikitlearn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "tf-idf": "TF-IDF",
    "tfidf": "TF-IDF",
    "cosine similarity": "Cosine Similarity",
    "system design": "System Design",
    "distributed systems": "Distributed Systems",
    "cross-functional collaboration": "Cross-Functional Collaboration",
    "problem solving": "Problem Solving",
    "team leadership": "Team Leadership",
    "project management": "Project Management"
}

# Flat list of all unique skills
ALL_SKILLS = []
for category_skills in SKILL_TAXONOMY.values():
    for skill in category_skills:
        if skill not in ALL_SKILLS:
            ALL_SKILLS.append(skill)

def get_skill_category(skill_name: str) -> str:
    """Find the category for a given skill."""
    for category, skills in SKILL_TAXONOMY.items():
        if skill_name in skills or any(s.lower() == skill_name.lower() for s in skills):
            return category
    return "Other Technical Skills"
