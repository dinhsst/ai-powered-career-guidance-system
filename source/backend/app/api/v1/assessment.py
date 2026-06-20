from fastapi import APIRouter, Depends, HTTPException
from app.schemas.assessment import AssessmentRequest, AssessmentResponse, CareerRecommendation
from app.ml.classifier import career_classifier
import numpy as np

router = APIRouter()

CAREER_NAMES = {
    "CNTT": "Công nghệ thông tin",
    "Kinh_te": "Kinh tế - Quản trị kinh doanh",
    "Su_pham": "Sư phạm",
    "Y_khoa": "Y khoa - Dược",
    "Nghe_thuat": "Nghệ thuật - Thiết kế",
}


@router.post("/submit", response_model=AssessmentResponse)
async def submit_assessment(request: AssessmentRequest):
    """
    Nhận kết quả trắc nghiệm Holland và điểm học tập để tạo gợi ý nghề nghiệp bằng AI.
    Mỗi gợi ý có kèm diễn giải dựa trên SHAP.
    """
    features = {
        "realistic": request.holland_scores.realistic,
        "investigative": request.holland_scores.investigative,
        "artistic": request.holland_scores.artistic,
        "social": request.holland_scores.social,
        "enterprising": request.holland_scores.enterprising,
        "conventional": request.holland_scores.conventional,
        "math_score": request.subject_scores.toan,
        "science_score": max(
            request.subject_scores.vat_ly or 0,
            request.subject_scores.hoa_hoc or 0,
        ),
        "literature_score": request.subject_scores.ngu_van,
        "financial_level": request.financial_level,
    }

    raw_results = career_classifier.predict(features)

    # Xác định mã Holland trội
    holland_dict = request.holland_scores.model_dump()
    top_holland = sorted(holland_dict.items(), key=lambda x: x[1], reverse=True)[:2]
    holland_code = "".join([k[0].upper() for k, _ in top_holland])

    recommendations = [
        CareerRecommendation(
            career_code=r["career_code"],
            career_name=CAREER_NAMES.get(r["career_code"], r["career_code"]),
            confidence=r["confidence"],
            explanation=r["explanation"],
            shap_factors=r.get("shap_factors"),
        )
        for r in raw_results
    ]

    return AssessmentResponse(
        recommendations=recommendations,
        holland_code=holland_code,
        mode="fallback" if career_classifier.model is None else "ml",
    )
