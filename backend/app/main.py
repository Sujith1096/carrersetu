import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, SessionLocal, engine
from app.routers import auth, analyze, history, stats, samples, jarvis, jobs
from app.services.job_aggregator import job_aggregator
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: safely initialize database and seed baseline data if empty."""
    # Enforce security credential verification (fails safely in production if JWT_SECRET missing)
    from app.services.auth import get_jwt_secret
    get_jwt_secret()

    init_db()
    db = SessionLocal()
    try:
        samples.seed_demo_data(db)
        job_aggregator.ensure_seed_data(db)
    except Exception as e:
        print(f"[WARN] Lifespan initialization notice: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title="CareerSetu – AI Career Intelligence Platform",
    description="Full-stack AI platform for resume parsing, TF-IDF cosine similarity job matching, explainable ATS scoring, and J.A.R.V.I.S. assistant.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration supporting local development and production deployments
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

env_cors = os.getenv("CORS_ORIGINS", "").strip()
if env_cors:
    parsed_origins = [orig.strip() for orig in env_cors.split(",") if orig.strip()]
    allowed_origins = list(set(DEFAULT_ORIGINS + parsed_origins))
    allow_all_creds = True
else:
    # Local fallback
    allowed_origins = DEFAULT_ORIGINS + ["*"]
    allow_all_creds = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_all_creds,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global Exception Handler: Sanitize unhandled exceptions in production
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    print(f"[ERROR] Unhandled exception on {request.method} {request.url.path}: {error_msg}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred while processing your request. Please try again or contact support."
        }
    )

# Register routers
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(stats.router)
app.include_router(samples.router)
app.include_router(jarvis.router)
app.include_router(jobs.router)

@app.get("/api/health")
def health_check():
    """
    System health check and diagnostic status.
    Returns HTTP 200 when healthy, or HTTP 503 when critical database connectivity fails.
    """
    db_status = "connected"
    is_healthy = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        is_healthy = False

    if not is_healthy:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "CareerSetu API",
                "version": "1.0.0",
                "database": db_status,
                "error": "Critical database connectivity failure. Service is unavailable."
            }
        )

    return {
        "status": "healthy",
        "service": "CareerSetu API",
        "version": "1.0.0",
        "database": db_status,
        "engine": "TF-IDF + Cosine Similarity + PyMuPDF",
        "environment": os.getenv("ENVIRONMENT", "production" if os.getenv("RENDER") else "development")
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT") == "development"
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
