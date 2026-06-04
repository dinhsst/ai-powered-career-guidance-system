from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import assessment, chat, careers, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load ML models, init vectorstore
    from app.ml.classifier import career_classifier
    from app.rag.pipeline import rag_pipeline
    career_classifier.load()
    await rag_pipeline.initialize()
    yield
    # Shutdown: cleanup resources


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Hệ thống tư vấn hướng nghiệp thông minh sử dụng AI",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(assessment.router, prefix="/api/v1/assessment", tags=["Assessment"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chat"])
app.include_router(careers.router, prefix="/api/v1/careers", tags=["Careers"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
