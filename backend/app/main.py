from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, SessionLocal
from app.routers import analyze, history, stats, samples, jarvis, jobs
from app.services.job_aggregator import job_aggregator

# Initialize database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-seed sample records on startup if database is empty
    db = SessionLocal()
    try:
        samples.seed_demo_data(db)
        job_aggregator.ensure_seed_data(db)
    except Exception as e:
        print(f"Auto-seed notice: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title="CareerSetu – AI Career Intelligence Platform",
    description="Full-stack AI platform for resume parsing, TF-IDF cosine similarity job matching, and explainable ATS scoring.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(stats.router)
app.include_router(samples.router)
app.include_router(jarvis.router)
app.include_router(jobs.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareerSetu API",
        "version": "1.0.0",
        "engine": "TF-IDF + Cosine Similarity + PyMuPDF"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
