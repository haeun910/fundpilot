import json
from fastapi import APIRouter, HTTPException
from apps.api.core.config import DATA_DIR

router = APIRouter(prefix="/funds", tags=["정책자금"])

_fund_cache: dict | None = None


def _load() -> dict:
    global _fund_cache
    if _fund_cache is None:
        _fund_cache = json.loads((DATA_DIR / "fund_info.json").read_text(encoding="utf-8"))
    return _fund_cache


@router.get("", summary="전체 정책자금 목록")
async def list_funds():
    data = _load()
    return {
        "quarter":     data["quarter"],
        "base_rate":   data["base_rate"],
        "total":       data["total_funds"],
        "funds":       data["funds"],
    }


@router.get("/{fund_id}", summary="정책자금 상세")
async def get_fund(fund_id: str):
    data  = _load()
    funds = {f["id"]: f for f in data["funds"]}
    if fund_id not in funds:
        raise HTTPException(status_code=404, detail=f"자금 ID '{fund_id}' 없음")
    return funds[fund_id]


@router.get("/{fund_id}/pattern", summary="정책자금 수혜 패턴")
async def get_pattern(fund_id: str):
    patterns = json.loads((DATA_DIR / "fund_patterns.json").read_text(encoding="utf-8"))["patterns"]
    if fund_id not in patterns:
        raise HTTPException(status_code=404, detail=f"패턴 데이터 없음: {fund_id}")
    pat = patterns[fund_id]
    pat.pop("feature_vector", None)   # 벡터는 내부 전용
    return pat
