"""
Rule-based fallback when LLM/RAG is unavailable.
Implements Robustness requirement: system never fully fails.
"""
from typing import Dict, Optional


HOLLAND_TO_CAREERS = {
    "R": ["Kỹ thuật cơ khí", "Xây dựng", "Điện - Điện tử", "Lâm nghiệp"],
    "I": ["Công nghệ thông tin", "Khoa học dữ liệu", "Y khoa", "Nghiên cứu khoa học"],
    "A": ["Thiết kế đồ họa", "Kiến trúc", "Âm nhạc", "Báo chí - Truyền thông"],
    "S": ["Sư phạm", "Công tác xã hội", "Tâm lý học", "Y tế cộng đồng"],
    "E": ["Kinh doanh", "Marketing", "Luật", "Quản trị doanh nghiệp"],
    "C": ["Kế toán", "Tài chính - Ngân hàng", "Hành chính", "Thống kê"],
}


def rule_based_response(question: str, context: Optional[Dict] = None) -> Dict:
    """
    Basic career guidance when AI services are unavailable.
    Returns structured response based on pre-defined rules.
    """
    base_careers = []

    if context and context.get("holland_code"):
        code = context["holland_code"].upper()
        for char in code[:2]:
            base_careers.extend(HOLLAND_TO_CAREERS.get(char, []))

    if not base_careers:
        base_careers = ["Công nghệ thông tin", "Kinh doanh", "Sư phạm", "Y tế", "Kỹ thuật"]

    answer = (
        "Hệ thống AI đang tạm thời bận. Dựa trên thông tin bạn cung cấp, "
        f"một số ngành nghề có thể phù hợp: {', '.join(base_careers[:3])}. "
        "Vui lòng thử lại sau để nhận tư vấn chi tiết hơn từ AI."
    )

    return {
        "answer": answer,
        "sources": [],
        "mode": "fallback",
        "careers": base_careers[:3],
    }
