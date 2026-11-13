import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Determine database URL from environment or fallback to SQLite
RAW_DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

if RAW_DATABASE_URL:
    # Normalize legacy "postgres://" to modern SQLAlchemy "postgresql://"
    if RAW_DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = RAW_DATABASE_URL
else:
    DEFAULT_DB_FILE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        "careersetu.db"
    )
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_FILE}"

# Engine configuration tailored to database dialect
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Production PostgreSQL connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency for thread-safe database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Safely initialize database tables without deleting existing records."""
    try:
        Base.metadata.create_all(bind=engine)
        print(f"[INFO] Database initialized successfully ({'SQLite' if 'sqlite' in DATABASE_URL else 'PostgreSQL'}).")
    except Exception as e:
        is_prod = os.getenv("ENVIRONMENT") == "production" or not DATABASE_URL.startswith("sqlite")
        if is_prod:
            print(f"[FATAL] Critical: Production database failed to initialize: {e}")
            raise RuntimeError(f"Production database initialization failed: {e}")
        else:
            print(f"[WARN] Database initialization notice: {e}")
