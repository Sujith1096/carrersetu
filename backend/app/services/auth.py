import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

def is_production() -> bool:
    """Detect if running in production environment."""
    env = os.getenv("ENVIRONMENT", "").lower().strip()
    if env in ["production", "prod"]:
        return True
    render_val = os.getenv("RENDER", "").lower().strip()
    if render_val and render_val not in ["false", "0", "no"]:
        return True
    db_url = os.getenv("DATABASE_URL", "").lower().strip()
    if db_url and not (db_url.startswith("sqlite") or "careersetu.db" in db_url):
        return True
    return False

def get_jwt_secret() -> str:
    """
    Retrieve JWT secret key with strict production security enforcement.
    In production: Requires JWT_SECRET to be configured (min 32 characters); fails safely if missing.
    In local development: Allows dev-only fallback if not explicitly provided.
    """
    secret = os.getenv("JWT_SECRET")
    if is_production():
        if not secret or len(secret.strip()) < 32:
            raise RuntimeError(
                "[FATAL] JWT_SECRET environment variable is missing or insufficiently secure in production. "
                "A secret of at least 32 characters is required for secure authentication."
            )
        return secret.strip()

    # Local development fallback only
    if secret and secret.strip():
        return secret.strip()
    return "dev_insecure_jwt_secret_key_only_for_local_debugging_32chars"

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 14

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

def hash_password(password: str) -> str:
    """Securely hash a plain text password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token for an authenticated user."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=JWT_EXPIRE_DAYS))
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency: Strictly enforces authentication.
    Raises 401 Unauthorized if missing, expired, or invalid.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in or provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or has been deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    FastAPI dependency: Resolves user if Bearer token is provided.
    Returns None if unauthenticated (allows guest resume evaluation).
    """
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return None
    try:
        user_id = int(payload["sub"])
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    except Exception:
        return None
