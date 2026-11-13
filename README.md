# CareerSetu – AI Career Intelligence Platform
### With J.A.R.V.I.S. – Personal AI Career Strategist & Global Jobs Explorer

A production-ready, commercial-grade full-stack platform that bridges the gap between candidate resumes and real-world job postings through genuine Natural Language Processing, TF-IDF vectorization, Cosine Similarity matching, explainable ATS scoring, a live Global Jobs & Companies Explorer, and an interactive **J.A.R.V.I.S.** holographic career mentor.

---

## 1. System Architecture

CareerSetu is built with a decoupled, high-performance architecture supporting both local development and cloud production deployments:

```
carrer_setu/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint, CORS handling, lifespan & safe auto-seed
│   │   ├── database.py           # Multi-DB engine (PostgreSQL connection pool + SQLite fallback)
│   │   ├── models.py             # SQLAlchemy models (AnalysisRecord, JobListing, CompanyProfile)
│   │   ├── schemas.py            # Pydantic v2 schemas for requests, responses & telemetry
│   │   ├── services/
│   │   │   ├── jarvis_engine.py  # J.A.R.V.I.S. multi-turn context engine (Cloud AI + Local Intelligence)
│   │   │   ├── job_aggregator.py # Multi-feed live sync (Remotive, Arbeitnow, Greenhouse) + caching
│   │   │   ├── pdf_parser.py     # PyMuPDF text stream extraction & section segmenter
│   │   │   ├── ml_engine.py      # TF-IDF, Cosine Similarity, Skill Extractor & ATS scorer
│   │   │   ├── skill_bank.py     # 200+ canonical technical & leadership skill taxonomies
│   │   │   └── recommendations.py# Prioritized actionable resume improvement advice
│   │   ├── routers/
│   │   │   ├── analyze.py        # /api/analyze/upload & /api/analyze/text (Validation & ATS)
│   │   │   ├── jobs.py           # /api/jobs, /api/companies, /api/jobs/sync (Search & sync)
│   │   │   ├── jarvis.py         # /api/jarvis/chat, /interview/start, /status & /config
│   │   │   ├── history.py        # /api/history audit records & detail queries
│   │   │   ├── stats.py          # /api/stats executive telemetry & distributions
│   │   │   └── samples.py        # /api/samples sample jobs & Alex Rivera PDF download
│   │   └── data/
│   │       ├── sample_data.py    # Curated job postings & sample candidate profile
│   │       └── Alex_Rivera_Resume.pdf  # Generated ATS-optimized PDF resume
│   ├── generate_sample_pdf.py    # Script generating sample PDF via ReportLab
│   ├── tests/
│   │   ├── test_production_audit.py # Security, CORS, rate limits, session isolation & health tests
│   │   ├── test_jobs_explorer.py # Automated integration tests for Jobs and Companies Explorer
│   │   ├── test_jarvis.py        # Automated test suite for JARVIS chat & mock interview engine
│   │   ├── test_ml_engine.py     # Unit test suite verifying ML algorithms & parsing
│   │   └── test_api_upload.py    # Integration test suite for PDF upload pipeline
│   ├── requirements.txt          # Python dependencies (FastAPI, PyMuPDF, Scikit-learn, Psycopg2)
│   ├── .env.example              # Backend environment template
│   └── careersetu.db             # Local SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Jarvis/
│   │   │   │   ├── JarvisVisualizer.jsx   # Holographic Arc-Reactor & frequency visualizer
│   │   │   │   ├── JarvisFloatingOrb.jsx  # Floating glowing orb accessible on all pages
│   │   │   │   └── JarvisChatPanel.jsx    # Futuristic Iron Man HUD slide-over panel
│   │   │   ├── Navbar.jsx        # Top banner with live API health indicator & JARVIS button
│   │   │   ├── Sidebar.jsx       # Dark forest green sidebar with active badges & page switcher
│   │   │   ├── MetricCard.jsx    # Executive stat cards with gold accents
│   │   │   ├── ScoreGauge.jsx    # Animated circular SVG ATS score meter
│   │   │   ├── SkillBadge.jsx    # Matching, missing, and additional skill pills
│   │   │   └── LoadingModal.jsx  # Multi-step ML processing progress modal
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx   # Luxury SaaS hero, feature cards & live demo CTA
│   │   │   ├── Dashboard.jsx     # Recharts score distribution & top skills telemetry
│   │   │   ├── JobsExplorerPage.jsx # Multi-filter live jobs database & 1-click ATS analyzer
│   │   │   ├── CompaniesExplorerPage.jsx # Global tech employers directory with openings count
│   │   │   ├── AnalyzePage.jsx   # PDF drag-and-drop, text mode, preset role loader
│   │   │   ├── ResultPage.jsx    # Comprehensive ATS report, breakdown & print mode
│   │   │   └── HistoryPage.jsx   # Persistent historical audit log with search & delete
│   │   ├── services/
│   │   │   └── api.js            # Environment-aware Fetch API client with session store
│   │   ├── App.jsx               # Master application coordinator with all routes
│   │   ├── index.css             # Tailwind directives & luxury styling
│   │   └── main.jsx
│   ├── vercel.json               # Vercel SPA routing rewrites
│   ├── tailwind.config.js        # Forest green (#123C2E), gold (#D4AF37) & cyan HUD
│   ├── vite.config.js            # Vite development proxy configuration
│   ├── package.json
│   └── .env.example              # Frontend environment template
├── render.yaml                   # Render Blueprint for FastAPI + Managed PostgreSQL
├── vercel.json                   # Root Vercel SPA configuration
├── .gitignore                    # Production git exclusion rules
├── .env.example                  # Root environment template
└── README.md
```

---

## 2. Key Features

### 1. ATS Explainable Scoring Engine
- **TF-IDF & Cosine Similarity:** Natural language vectorization comparing candidate experience against target role requirements.
- **200+ Canonical Skills Bank:** Categorizes matching, missing, and additional competencies.
- **Explainable 4-Factor Composite:** Skills Alignment (40%), Content Similarity (25%), Quantified Metrics & Action Verbs (20%), and Section Architecture (15%).
- **PyMuPDF Extraction:** Deep text stream parser with graceful handling for image-only/scanned documents.

### 2. J.A.R.V.I.S. AI Career Strategist
- **Context Awareness:** Automatically ingests candidate name, target role, ATS score, missing skills, and resume bullet points.
- **Interactive Mock Interview:** Delivers one question at a time (Architecture, System Design, STAR), evaluates responses with scores out of 10, and offers actionable critiques.
- **Session Isolation:** User API keys are stored in browser session storage and sent per-request. One user's session never overwrites another user's configuration.
- **Dual Engine:** Seamlessly uses Google Gemini, OpenAI, or Groq when keys are present, falling back to the autonomous local reasoning engine offline.

### 3. Global Jobs & Companies Explorer
- **Live Feed Integrations:** Sourced from Remotive, Arbeitnow, and Greenhouse public job boards (Cloudflare, GitLab, Discord).
- **Enterprise Companies Directory:** 40+ top global and Indian employers (Google, Microsoft, Amazon, Meta, TCS, Infosys, Wipro, Accenture, Nvidia, etc.) with active openings badges.
- **1-Click ATS Matcher Transfer:** Instant "Analyze with ATS" button pre-populates job title, company, and complete plain-text description directly into the Job Matcher without copy-pasting.
- **Sync Protection:** 60-second cooldown on the synchronization endpoint prevents external API flooding.

---

## 3. Environment Variables Reference

| Variable | Scope | Description | Default / Example |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Backend | Connection string for PostgreSQL or SQLite | `sqlite:///./careersetu.db` |
| `CORS_ORIGINS` | Backend | Comma-separated list of allowed frontend domains | `http://localhost:5173,https://careersetu.vercel.app` |
| `ENVIRONMENT` | Backend | Application environment (`development` / `production`) | `development` |
| `PORT` | Backend | HTTP port assigned by hosting platform | `8000` |
| `HOST` | Backend | Network interface to bind | `0.0.0.0` |
| `GEMINI_API_KEY` | Backend | Optional: Google Gemini API key for J.A.R.V.I.S. | *(empty - local engine default)* |
| `OPENAI_API_KEY` | Backend | Optional: OpenAI GPT-4o API key | *(empty)* |
| `GROQ_API_KEY` | Backend | Optional: Groq Llama-3.3 API key | *(empty)* |
| `VITE_API_URL` | Frontend | Backend API base URL for production Vercel | `https://careersetu-backend.onrender.com` |

---

## 4. Local Development Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (tested on Node.js v24)
- npm 9+

### Step 1: Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend runs at `http://127.0.0.1:8000` (Interactive API docs at `http://127.0.0.1:8000/docs`).*

### Step 2: Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs at `http://localhost:5173` with automatic Vite proxy to the backend.*

---

## 5. Automated Test Suites

Run all backend verification suites:

```bash
cd backend

# 1. Production Security, CORS, Rate Limiting & Health:
python -m unittest tests/test_production_audit.py

# 2. Global Jobs & Companies Explorer API:
python -m unittest tests/test_jobs_explorer.py

# 3. TF-IDF ML Engine & ATS Scoring:
python tests/test_ml_engine.py

# 4. J.A.R.V.I.S. Reasoning & Mock Interviews:
python tests/test_jarvis.py

# 5. PDF Upload Pipeline & SQLite Persistence:
python tests/test_api_upload.py
```

Frontend production build check:
```bash
cd frontend
npm run build
npm run lint
```

---

## 6. Step-by-Step Production Deployment Guide

### A. Deploy Backend & Database on Render

1. **Create Managed PostgreSQL Database:**
   - Log in to your [Render Dashboard](https://dashboard.render.com).
   - Click **New +** > **PostgreSQL**.
   - Name: `careersetu-postgres`.
   - Region: Select closest to your users (e.g., `Oregon (US West)`).
   - Click **Create Database**.
   - Once created, copy the **Internal Database URL** (for Render services) or **External Database URL**.

2. **Deploy FastAPI Web Service:**
   - In Render Dashboard, click **New +** > **Web Service**.
   - Connect your GitHub repository (`Sujith1096/carrersetu`).
   - Configure the service settings:
     - **Name:** `careersetu-backend`
     - **Root Directory:** `backend`
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Health Check Path:** `/api/health`
   - Add **Environment Variables**:
     - `DATABASE_URL` = Paste your Render PostgreSQL connection string (Render will auto-link if using blueprints).
     - `CORS_ORIGINS` = `http://localhost:5173,https://<your-vercel-domain>.vercel.app`
     - `ENVIRONMENT` = `production`
     - *(Optional)* `GEMINI_API_KEY` = Your Google AI Studio key.
   - Click **Deploy Web Service**.
   - Note your backend URL (e.g., `https://careersetu-backend.onrender.com`).

*(Alternative: You can also deploy via the included `render.yaml` Blueprint directly from Render Dashboard).*

---

### B. Deploy Frontend on Vercel

1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** > **Project** and import your repository (`Sujith1096/carrersetu`).
3. Configure project settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Edit and set to `frontend` (or leave root since `vercel.json` handles both).
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add **Environment Variable**:
   - `VITE_API_URL` = `https://careersetu-backend.onrender.com` (Your Render backend URL).
5. Click **Deploy**.
6. Once deployed, copy your production Vercel URL (e.g., `https://careersetu.vercel.app`) and ensure it is included in the backend's `CORS_ORIGINS` environment variable.

---

## 7. Portfolio Presentation Checklist

- [x] Full-stack architecture with decoupled frontend and backend.
- [x] Genuine NLP text preprocessing, TF-IDF vectorization, and Cosine Similarity (no random scores).
- [x] PyMuPDF PDF parsing with error handling for scanned/unreadable documents.
- [x] Explainable 4-component ATS scoring formula with clear breakdowns.
- [x] Live Global Jobs Explorer with real-time filters and live sync from public feeds.
- [x] Companies Directory with live openings counters.
- [x] J.A.R.V.I.S. conversational mentor with interactive mock interviews.
- [x] PostgreSQL & SQLite dual-database support with safe migrations.
- [x] Isolated client-side session security preventing cross-user key leaks.
- [x] Production deployment configuration for Vercel and Render.
