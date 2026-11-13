from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status

from app.services.jarvis_engine import jarvis_engine

router = APIRouter(prefix="/api/jarvis", tags=["JARVIS AI"])

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class JarvisChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    context: Optional[Dict[str, Any]] = None
    interview_state: Optional[Dict[str, Any]] = None

class JarvisChatResponse(BaseModel):
    reply: str
    mode: str          # "live_api" | "local_intelligence"
    provider: str      # e.g. "Google Gemini", "JARVIS Autonomous Intelligence Engine"
    updated_name: Optional[str] = None
    interview_state: Optional[Dict[str, Any]] = None
    suggested_replies: List[str] = []

class KeyConfigRequest(BaseModel):
    provider: str  # "gemini" | "openai" | "groq"
    api_key: str

@router.post("/chat", response_model=JarvisChatResponse)
def jarvis_chat(payload: JarvisChatRequest):
    """
    Main communication channel with J.A.R.V.I.S.
    Context-aware AI mentor for resume optimization, interview prep, and technical queries.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    # Convert history
    history_dicts = [{"role": m.role, "content": m.content} for m in (payload.conversation_history or [])]
    
    result = jarvis_engine.generate_response(
        message=payload.message.strip(),
        conversation_history=history_dicts,
        context=payload.context,
        interview_state=payload.interview_state
    )

    return JarvisChatResponse(
        reply=result["reply"],
        mode=result["mode"],
        provider=result["provider"],
        updated_name=result.get("updated_name"),
        interview_state=result.get("interview_state"),
        suggested_replies=result.get("suggested_replies", [])
    )

@router.post("/interview/start", response_model=JarvisChatResponse)
def start_interview(context: Optional[Dict[str, Any]] = None):
    """Direct trigger to initiate interactive interview mode."""
    result = jarvis_engine._start_mock_interview(context)
    return JarvisChatResponse(
        reply=result["reply"],
        mode=result["mode"],
        provider=result["provider"],
        interview_state=result.get("interview_state"),
        suggested_replies=result.get("suggested_replies", [])
    )

@router.get("/status")
def get_jarvis_status():
    """Check whether JARVIS is running via Cloud API or Local Intelligence Engine."""
    provider, key = jarvis_engine.get_active_provider()
    if provider and key:
        return {
            "mode": "live_api",
            "provider": provider.upper(),
            "has_key": True,
            "description": f"Connected to {provider.upper()} cloud neural model."
        }
    return {
        "mode": "local_intelligence",
        "provider": "JARVIS Autonomous Engine",
        "has_key": False,
        "description": "Running CareerSetu Local Intelligence Engine with full context awareness (No external API key set)."
    }

@router.post("/config")
def set_api_key(payload: KeyConfigRequest):
    """Optional: Configure cloud AI provider key during the active session."""
    if not payload.api_key.strip():
        jarvis_engine.clear_session_key()
        return {"status": "reset", "message": "Reverted to JARVIS Local Intelligence Engine."}

    jarvis_engine.set_session_key(payload.provider, payload.api_key)
    return {
        "status": "configured",
        "provider": payload.provider,
        "message": f"Successfully activated {payload.provider.upper()} cloud intelligence for JARVIS."
    }
