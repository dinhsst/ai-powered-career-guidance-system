from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1 import assessment, chat, careers, auth
from app.models.user import User


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load ML models, init vectorstore
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.warning("Không thể khởi tạo bảng cơ sở dữ liệu: %s", exc)

    from app.ml.classifier import career_classifier
    from app.rag.pipeline import rag_pipeline
    career_classifier.load()
    await rag_pipeline.initialize()
    yield
    # Shutdown: cleanup resources


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Nền tảng tư vấn hướng nghiệp thông minh dành cho học sinh Việt Nam",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Xác thực"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["Đánh giá"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Trò chuyện AI"])
app.include_router(careers.router, prefix="/api/v1/careers", tags=["Ngành nghề"])


@app.get("/health")
async def health_check():
    return {"status": "hoat_dong", "app": settings.APP_NAME}
