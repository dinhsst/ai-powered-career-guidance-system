import logging

from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.rag.pipeline import rag_pipeline
import uuid
from app.llm.prompts import CAREER_ADVISOR_SYSTEM_PROMPT

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    API trò chuyện tư vấn hướng nghiệp bằng AI.
    Sử dụng pipeline RAG với Gemini, tự động fallback khi dịch vụ AI không khả dụng.
    Nội dung đầu vào được kiểm tra prompt injection trước khi xử lý.
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Tạo câu hỏi có ngữ cảnh
    question = request.message
    if request.user_context:
        context_prefix = _build_context_prefix(request.user_context)
        question = f"{context_prefix}\n\nCâu hỏi: {request.message}"
    # Add system prompt before the question
    #full_prompt = f"{CAREER_ADVISOR_SYSTEM_PROMPT}\n\n{question}"    
    logging.info(f"Nhận câu hỏi: {question} (session: {session_id})")
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
