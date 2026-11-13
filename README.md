# CareerSetu – AI Career Intelligence Platform
### With J.A.R.V.I.S. – Personal AI Career Strategist & Holographic Mentor

A full-stack, commercial-grade web platform that bridges the gap between candidate resumes and job postings through genuine Natural Language Processing, TF-IDF vectorization, Cosine Similarity matching, explainable ATS scoring, and an interactive **J.A.R.V.I.S.** AI career mentor.

---

## 1. Architecture Overview

CareerSetu is built with a decoupled modern architecture:

```
carrer_setu/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application entrypoint with CORS, lifespan & auto-seed
│   │   ├── database.py           # SQLite connection & declarative base
│   │   ├── models.py             # SQLAlchemy models for persistent reports
│   │   ├── schemas.py            # Pydantic schemas for requests, responses & stats
│   │   ├── services/
│   │   │   ├── jarvis_engine.py  # J.A.R.V.I.S. multi-turn context engine (Cloud AI + Local Intelligence)
│   │   │   ├── pdf_parser.py     # PyMuPDF text stream extraction & section segmenter
│   │   │   ├── ml_engine.py      # TF-IDF, Cosine Similarity, Skill Extractor & ATS scorer
│   │   │   ├── skill_bank.py     # 200+ canonical technical & leadership skill taxonomies
│   │   │   └── recommendations.py# Prioritized actionable resume improvement advice
│   │   ├── routers/
│   │   │   ├── jarvis.py         # /api/jarvis/chat, /interview/start & /status
│   │   │   ├── analyze.py        # /api/analyze/upload & /api/analyze/text
│   │   │   ├── history.py        # /api/history CRUD operations
│   │   │   ├── stats.py          # /api/stats dashboard telemetry
│   │   │   └── samples.py        # /api/samples pre-loaded jobs & PDF downloads
│   │   └── data/
│   │       ├── sample_data.py    # Curated job postings & sample candidate profile
│   │       └── Alex_Rivera_Resume.pdf  # Generated ATS-optimized PDF resume
│   ├── generate_sample_pdf.py    # Script generating sample PDF via ReportLab
│   ├── tests/
│   │   ├── test_jarvis.py        # Automated test suite for JARVIS chat & interview flow
│   │   ├── test_ml_engine.py     # Unit test suite verifying ML algorithms & parsing
│   │   └── test_api_upload.py    # Integration test suite for PDF upload pipeline
│   ├── requirements.txt
│   └── careersetu.db             # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Jarvis/
│   │   │   │   ├── JarvisVisualizer.jsx   # Holographic Arc-Reactor & frequency visualizer
│   │   │   │   ├── JarvisFloatingOrb.jsx  # Floating glowing orb fixed on all pages
│   │   │   │   └── JarvisChatPanel.jsx    # Futuristic Iron Man HUD slide-over panel
│   │   │   ├── Navbar.jsx        # Top banner with live API health indicator & JARVIS button
│   │   │   ├── Sidebar.jsx       # Dark forest green sidebar with active badges & JARVIS trigger
│   │   │   ├── MetricCard.jsx    # Executive stat cards with gold accents
│   │   │   ├── ScoreGauge.jsx    # Animated circular SVG ATS score meter
│   │   │   ├── SkillBadge.jsx    # Matching, missing, and additional skill pills
│   │   │   └── LoadingModal.jsx  # Multi-step ML processing progress modal
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx   # Luxury SaaS hero, feature cards & live demo CTA
│   │   │   ├── Dashboard.jsx     # Recharts score distribution & top skills telemetry
│   │   │   ├── AnalyzePage.jsx   # PDF drag-and-drop, text mode, preset role loader
│   │   │   ├── ResultPage.jsx    # Comprehensive ATS report, breakdown & print mode
│   │   │   └── HistoryPage.jsx   # SQLite historical audit log with search & delete
│   │   ├── services/
│   │   │   └── api.js            # Fetch API client with error mapping
│   │   ├── App.jsx               # Master application coordinator with JARVIS integration
│   │   ├── index.css             # Tailwind directives & luxury styling
│   │   └── main.jsx
│   ├── tailwind.config.js        # Forest green (#123C2E), gold (#D4AF37) & cyan HUD
│   ├── vite.config.js            # Reverse proxy configuration to FastAPI
│   └── package.json
└── README.md
```

---

## 2. J.A.R.V.I.S. – AI Career Assistant

CareerSetu includes an Iron Man-inspired AI assistant named **J.A.R.V.I.S.** (Just A Rather Very Intelligent System):

### Key Capabilities:
1. **Context-Aware Intelligence:** Ingests active candidate resume text, target role, company, exact ATS score, component weights, matching skills, and missing competencies.
2. **Interactive Mock Interview Mode:**
   - Asks one tailored interview question at a time (Technical Architecture, System Design, or Behavioral STAR).
   - Evaluates the user's answer: calculates a score out of 10, pinpoints strengths, provides constructive critiques, and advances to the next question.
3. **Resume & ATS Optimization:** Pinpoints why scores fell in specific categories and drafts revised bullet points using the Google XYZ formula (*Accomplished [X] measured by [Y] doing [Z]*).
4. **Custom 30-Day Roadmaps:** Analyzes the user's specific missing skills and formulates a week-by-week learning plan with milestones.
5. **Master Project Pitch:** Helps candidates explain projects (e.g. CareerSetu or past enterprise initiatives) using the Problem-Architecture-Hurdle-Result framework.
6. **Technical Q&A:** Explains Python, SQL indexing, FastAPI async patterns, React rendering optimizations, Docker, and distributed systems with syntax-highlighted code blocks.
7. **Transparent Dual-Mode Engine:**
   - **Local Autonomous Intelligence Mode (Default):** Runs immediately with 0 external API keys, analyzing real context data and providing personalized mentorship.
   - **Cloud AI Mode (Optional):** Supports Google Gemini, OpenAI, and Groq by configuring a key in the settings drawer.
8. **Holographic Audio Synthesis:** Integrates browser Speech Synthesis (`window.speechSynthesis`) to voice responses in a refined assistant persona.

---

## 3. Technology Stack

- **Frontend:** React 19, Vite 8, Tailwind CSS 3.4, Recharts, React-Markdown, Lucide Icons, Canvas-Confetti
- **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy
- **NLP / Machine Learning:** Scikit-learn (TF-IDF, Cosine Similarity), NumPy
- **Document Processing:** PyMuPDF (`pymupdf`), ReportLab
- **Database:** SQLite (`careersetu.db`)

---

## 4. Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (tested on Node.js v24)
- npm 9+

### Step 1: Install Backend Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### Step 2: Generate the Sample PDF Resume (Optional)
```bash
python generate_sample_pdf.py
```

### Step 3: Run Backend Tests
```bash
python tests/test_jarvis.py
python tests/test_ml_engine.py
python tests/test_api_upload.py
```

### Step 4: Start the FastAPI Backend
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend runs at `http://127.0.0.1:8000` (Swagger UI at `http://127.0.0.1:8000/docs`).*

### Step 5: Install Frontend Dependencies & Start Server
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs at `http://127.0.0.1:5173` with reverse proxy to the backend.*

---

## 5. Testing Summary

| Test Case | Method | Expected Output | Status |
| :--- | :--- | :--- | :--- |
| **JARVIS Status Endpoint** | `GET /api/jarvis/status` | Verified mode and provider status | **PASSED** |
| **Context-Aware Chat** | `POST /api/jarvis/chat` | Personalizes response to candidate & ATS score | **PASSED** |
| **Mock Interview Flow** | `POST /api/jarvis/interview/start` | Role-based questions & answer evaluation (score /10) | **PASSED** |
| **PyMuPDF Extraction** | `tests/test_ml_engine.py` | Full text, candidate name, email, phone | **PASSED** |
| **TF-IDF & Cosine Similarity** | `tests/test_ml_engine.py` | Mathematical cosine similarity calculation | **PASSED** |
| **PDF Upload API via Proxy** | `POST /api/analyze/upload` | 200 OK, full report, SQLite ID assigned | **PASSED** |
| **Frontend Production Build** | `npm run build` | Zero syntax/import errors, fast bundle | **PASSED** |
