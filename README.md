# 🎯 AI-Powered Career Guidance System
Hệ thống tư vấn hướng nghiệp thông minh sử dụng AI — Đồ án môn Tư duy AI

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌──────────────────────────────────────┐
│   Angular 17    │───▶│          FastAPI Backend              │
│   (Frontend)    │    │  ┌──────────┐  ┌───────────────────┐ │
│                 │    │  │ ML Core  │  │   RAG Pipeline    │ │
│ - Assessment    │    │  │(Sklearn) │  │ LangChain+Gemini  │ │
│ - Chat UI       │    │  └──────────┘  └───────────────────┘ │
│ - Results +     │    │  ┌──────────┐  ┌───────────────────┐ │
│   XAI Charts    │    │  │Guardrails│  │  Fallback (Rules) │ │
└─────────────────┘    │  └──────────┘  └───────────────────┘ │
                        └──────────────────────────────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │        ChromaDB              │
                         │  (Career/University Vector   │
                         │        Knowledge Base)       │
                         └─────────────────────────────┘
```

## 🚀 Chạy dự án

### Prerequisites
- Node.js 20+, Angular CLI 17+
- Python 3.11+
- Docker & Docker Compose (tuỳ chọn)

### Backend
```bash
cd backend
cp .env.example .env   # Điền GOOGLE_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
ng serve
# App: http://localhost:4200
```

### Docker (tất cả services)
```bash
cp backend/.env.example backend/.env  # Điền API keys
docker-compose up --build
```

## 📁 Cấu trúc thư mục

```
├── frontend/                    # Angular 17
│   └── src/app/
│       ├── core/services/       # API, Auth, Assessment, Chat services
│       └── features/
│           ├── assessment/      # Trắc nghiệm Holland + điểm số
│           ├── chat/            # Chat với AI tư vấn
│           ├── results/         # Kết quả + biểu đồ XAI
│           └── auth/            # Đăng nhập / Đăng ký
├── backend/                     # FastAPI
│   └── app/
│       ├── api/v1/              # Endpoints: assessment, chat, careers, auth
│       ├── core/                # Config, Security, Guardrails
│       ├── ml/                  # Scikit-learn classifier + SHAP explainer
│       ├── rag/                 # LangChain RAG pipeline
│       ├── llm/                 # Gemini client, prompts, fallback
│       └── schemas/             # Pydantic models
├── data/
│   ├── careers/                 # Danh mục ngành nghề (JSON)
│   ├── universities/            # Dữ liệu trường ĐH/CĐ (JSON)
│   └── market/                  # Báo cáo thị trường việc làm
└── docker-compose.yml
```

## 🛡️ Các tính năng AI Responsible

| Nguyên tắc | Giải pháp |
|---|---|
| **Reliability** | RAG + temperature=0.1 + Ragas evaluation |
| **Fairness** | Anti-bias system prompt + fairness-aware ML |
| **Robustness** | Guardrails input validation + rule-based fallback |
| **Social Impact** | Bộ lọc học phí, gợi ý học bổng, hệ CĐ nghề |
| **Explainability** | Chain-of-Thought prompting + SHAP/LIME XAI |

## 🔑 Biến môi trường

| Biến | Mô tả |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key từ [Google AI Studio](https://aistudio.google.com) |
| `SECRET_KEY` | JWT secret key |
| `DATABASE_URL` | PostgreSQL connection string |
