from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from app.core.guardrails import validate_score


class SubjectScores(BaseModel):
    toan: float = Field(..., ge=0, le=10, description="Điểm Toán")
    ngu_van: float = Field(..., ge=0, le=10, description="Điểm Ngữ Văn")
    tieng_anh: float = Field(..., ge=0, le=10, description="Điểm Tiếng Anh")
    vat_ly: Optional[float] = Field(None, ge=0, le=10)
    hoa_hoc: Optional[float] = Field(None, ge=0, le=10)
    sinh_hoc: Optional[float] = Field(None, ge=0, le=10)
    lich_su: Optional[float] = Field(None, ge=0, le=10)
    dia_ly: Optional[float] = Field(None, ge=0, le=10)


class HollandScores(BaseModel):
    realistic: float = Field(..., ge=0, le=1, description="Thực tế (R)")
    investigative: float = Field(..., ge=0, le=1, description="Nghiên cứu (I)")
    artistic: float = Field(..., ge=0, le=1, description="Nghệ thuật (A)")
    social: float = Field(..., ge=0, le=1, description="Xã hội (S)")
    enterprising: float = Field(..., ge=0, le=1, description="Doanh nghiệp (E)")
    conventional: float = Field(..., ge=0, le=1, description="Quy tắc (C)")


class AssessmentRequest(BaseModel):
    subject_scores: SubjectScores
    holland_scores: HollandScores
    financial_level: int = Field(..., ge=1, le=3, description="1=Thấp, 2=Trung bình, 3=Cao")
    preferred_regions: Optional[List[str]] = None
    target_education_level: Optional[str] = None  # "university", "college", "vocational"


class CareerRecommendation(BaseModel):
    career_code: str
    career_name: str
    confidence: float
    explanation: str
    shap_factors: Optional[dict] = None


class AssessmentResponse(BaseModel):
    recommendations: List[CareerRecommendation]
    holland_code: str
    mode: str  # "ml" or "fallback"
    suggested_universities: Optional[List[dict]] = None
