from fastapi import APIRouter, Query
from typing import Optional, List

router = APIRouter()

# Dữ liệu mẫu, sẽ thay bằng dữ liệu từ cơ sở dữ liệu hoặc tệp JSON
SAMPLE_CAREERS = [
    {"code": "CNTT", "name": "Công nghệ thông tin", "holland_codes": ["I", "R"], "avg_salary": "15-30 triệu/tháng", "demand": "Rất cao"},
    {"code": "Y_khoa", "name": "Y khoa", "holland_codes": ["I", "S"], "avg_salary": "20-50 triệu/tháng", "demand": "Cao"},
    {"code": "Su_pham", "name": "Sư phạm", "holland_codes": ["S", "A"], "avg_salary": "8-15 triệu/tháng", "demand": "Trung bình"},
    {"code": "Kinh_te", "name": "Kinh tế - QTKD", "holland_codes": ["E", "C"], "avg_salary": "12-25 triệu/tháng", "demand": "Cao"},
]


@router.get("/list")
async def list_careers(
    holland_code: Optional[str] = Query(None, description="Lọc theo mã Holland (R/I/A/S/E/C)"),
    demand: Optional[str] = Query(None, description="Nhu cầu: Cao/Trung bình"),
):
    careers = SAMPLE_CAREERS
    if holland_code:
        careers = [c for c in careers if holland_code.upper() in c["holland_codes"]]
    if demand:
        careers = [c for c in careers if demand in c["demand"]]
    return {"careers": careers, "total": len(careers)}


@router.get("/{career_code}")
async def get_career_detail(career_code: str):
    career = next((c for c in SAMPLE_CAREERS if c["code"] == career_code), None)
    if not career:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Ngành '{career_code}' không tồn tại")
    return career
