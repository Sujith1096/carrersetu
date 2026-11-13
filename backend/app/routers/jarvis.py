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
    client_provider: Optional[str] = None
    client_api_key: Optional[str] = None

class InterviewStartRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None
    client_provider: Optional[str] = None
    client_api_key: Optional[str] = None

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

    if payload.client_provider:
        norm_provider = payload.client_provider.lower().strip()
        if norm_provider not in ["gemini", "openai", "groq"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported AI provider '{payload.client_provider}'. Supported providers are: gemini, openai, groq."
            )

    # Convert history
    history_dicts = [{"role": m.role, "content": m.content} for m in (payload.conversation_history or [])]
    
    result = jarvis_engine.generate_response(
        message=payload.message.strip(),
        conversation_history=history_dicts,
        context=payload.context,
        interview_state=payload.interview_state,
        client_provider=payload.client_provider,
        client_api_key=payload.client_api_key
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
def start_interview(payload: Optional[InterviewStartRequest] = None):
    """Direct trigger to initiate interactive interview mode."""
    ctx = payload.context if payload else None
    client_provider = payload.client_provider if payload else None
    client_api_key = payload.client_api_key if payload else None

    if client_provider:
        norm_provider = client_provider.lower().strip()
        if norm_provider not in ["gemini", "openai", "groq"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported AI provider '{client_provider}'. Supported providers are: gemini, openai, groq."
            )

    result = jarvis_engine._start_mock_interview(
        context=ctx,
        client_provider=client_provider,
        client_api_key=client_api_key
    )
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
            "has_server_key": True,
            "description": f"Connected to {provider.upper()} cloud neural model configured on backend."
        }
    return {
        "mode": "local_intelligence",
        "provider": "JARVIS Autonomous Engine",
        "has_key": False,
        "has_server_key": False,
        "description": "Running CareerSetu Local Intelligence Engine with full context awareness (No server key configured)."
    }

@router.post("/config")
def set_api_key(payload: KeyConfigRequest):
    """Safely validate user's personal API key format for client session storage."""
    provider = payload.provider.lower().strip() if payload.provider else ""
    if provider not in ["gemini", "openai", "groq"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported AI provider '{payload.provider}'. Supported providers are: gemini, openai, groq."
        )

    key = payload.api_key.strip() if payload.api_key else ""
    if not key:
        return {"status": "reset", "message": "Reverted to JARVIS Local Intelligence Engine."}
    if len(key) < 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The provided API key appears too short or invalid. Please check your credentials."
        )
    return {
        "status": "configured",
        "provider": payload.provider,
        "message": f"{payload.provider.upper()} API key verified for current session."
    }
