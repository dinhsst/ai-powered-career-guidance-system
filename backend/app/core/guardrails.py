"""
Input validation guardrails to prevent prompt injection and harmful inputs.
Uses pattern-based detection; can be upgraded to NeMo Guardrails or Llama Guard.
"""
import re
from typing import Tuple

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions",
    r"you\s+are\s+now\s+(?!a\s+career)",
    r"act\s+as\s+(?!a\s+career)",
    r"jailbreak",
    r"DAN\s+mode",
    r"forget\s+your\s+(instructions|training|role)",
    r"<\s*script",
    r"system\s*prompt",
]

CAREER_TOPIC_KEYWORDS = [
    "nghề", "ngành", "học", "trường", "đại học", "cao đẳng", "việc làm",
    "hướng nghiệp", "tư vấn", "career", "university", "study", "job",
    "skill", "kỹ năng", "điểm số", "sở thích", "tính cách", "học bổng",
]


def check_prompt_injection(text: str) -> Tuple[bool, str]:
    """Returns (is_safe, reason)"""
    text_lower = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, "Nội dung vi phạm chính sách sử dụng hệ thống"
    return True, ""


def validate_score(score: float, field_name: str = "Điểm số") -> float:
    """Validate academic scores are within 0-10 range."""
    if not (0.0 <= score <= 10.0):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} phải nằm trong khoảng 0-10, nhận được: {score}"
        )
    return round(score, 1)


def sanitize_text_input(text: str, max_length: int = 2000) -> str:
    """Remove dangerous characters and limit length."""
    text = text.strip()[:max_length]
    text = re.sub(r'[<>{}]', '', text)
    return text
