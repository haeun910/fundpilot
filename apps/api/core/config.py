from pathlib import Path
from functools import lru_cache
import os

# 프로젝트 루트: apps/api/core/ 기준으로 3단계 위
_ROOT = Path(__file__).parents[3]


class Settings:
    app_name:    str  = "FundPilot API"
    debug:       bool = os.getenv("DEBUG", "false").lower() == "true"
    # DATA_DIR 환경변수가 없으면 프로젝트 루트 기준 절대경로로 fallback
    data_dir:    str  = os.getenv("DATA_DIR", str(_ROOT / "data" / "processed"))
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "https://fundpilot.vercel.app",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings  = get_settings()
DATA_DIR  = Path(settings.data_dir)
