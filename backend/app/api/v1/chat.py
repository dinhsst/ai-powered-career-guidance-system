from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.rag.pipeline import rag_pipeline
import uuid

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    AI career guidance chat endpoint.
    Uses RAG pipeline with Gemini, falls back to rule-based if unavailable.
    Input is validated against prompt injection before processing.
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Build context-aware question
    question = request.message
    if request.user_context:
        context_prefix = _build_context_prefix(request.user_context)
        question = f"{context_prefix}\n\nCâu hỏi: {request.message}"

    result = await rag_pipeline.query(question, request.user_context)

    return ChatResponse(
        reply=result["answer"],
        sources=result.get("sources", []),
        mode=result.get("mode", "unknown"),
        session_id=session_id,
    )


def _build_context_prefix(ctx: dict) -> str:
    parts = ["[Thông tin học sinh]"]
    if ctx.get("holland_code"):
        parts.append(f"Mã Holland: {ctx['holland_code']}")
    if ctx.get("financial_level"):
        levels = {1: "Khó khăn", 2: "Trung bình", 3: "Khá giả"}
        parts.append(f"Điều kiện kinh tế: {levels.get(ctx['financial_level'], 'Không rõ')}")
    if ctx.get("top_subjects"):
        parts.append(f"Môn mạnh: {', '.join(ctx['top_subjects'])}")
    return "\n".join(parts)
