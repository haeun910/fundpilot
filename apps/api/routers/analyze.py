import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from apps.api.schemas.models import RecommendRequest, FullAnalysisResponse
from apps.api.services import recommender, risk_analyzer
from apps.api.core.config import settings, DATA_DIR

router = APIRouter(prefix="/analyze", tags=["분석"])


def _get_base_rate() -> float | None:
    try:
        data = json.loads((DATA_DIR / "fund_info.json").read_text(encoding="utf-8"))
        return data.get("base_rate")
    except Exception:
        return None


@router.post("", response_model=FullAnalysisResponse, summary="전체 분석")
async def full_analyze(req: RecommendRequest):
    """
    기업 정보 입력 → 신청 가능 여부 + 추천 TOP N + 리스크 분석
    """
    try:
        profile, eligibility, recs = recommender.run(
            company=req.company,
            top_n=req.top_n,
            data_dir=settings.data_dir,
        )
        _, risk = risk_analyzer.run(
            company=req.company,
            fund_id=recs[0].fund_id if recs else None,
            data_dir=settings.data_dir,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FullAnalysisResponse(
        company_profile=profile,
        eligibility=eligibility,
        recommendations=recs,
        risk=risk,
        total=len(recs),
        base_rate=_get_base_rate(),
    )
