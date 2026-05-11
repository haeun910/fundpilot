import sys
from pathlib import Path

# 패키지 경로 설정
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "packages"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.core.config import settings
from apps.api.routers import analyze, funds

app = FastAPI(
    title=settings.app_name,
    description="중소벤처기업진흥공단 공공데이터 기반 정책자금 추천 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(analyze.router)
app.include_router(funds.router)


@app.get("/", tags=["상태"])
async def root():
    return {
        "service": settings.app_name,
        "status":  "running",
        "docs":    "/docs",
    }


@app.get("/health", tags=["상태"])
async def health():
    return {"status": "ok"}
