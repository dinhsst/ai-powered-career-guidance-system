from pydantic import BaseModel, field_validator
from typing import Optional
from app.core.guardrails import sanitize_text_input, check_prompt_injection
from fastapi import HTTPException


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_context: Optional[dict] = None  # holland_code, financial_level, etc.

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = sanitize_text_input(v, max_length=1000)
        is_safe, reason = check_prompt_injection(v)
        if not is_safe:
            raise ValueError(reason)
        return v


class ChatResponse(BaseModel):
    reply: str
    sources: list = []
    mode: str  # "rag", "llm", or "fallback"
    session_id: str
