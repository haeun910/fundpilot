"""
리스크 분석 오케스트레이터
isolation_model 호출 + 스키마 변환
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[4] / "packages"))

from ml.isolation_model import analyze as iso_analyze
from apps.api.schemas.models import CompanyInput, CompanyProfile, RiskResult
from apps.api.services.recommender import _build_profile


def run(
    company: CompanyInput,
    fund_id: str | None = None,
    data_dir: str = "data/processed",
) -> tuple[CompanyProfile, RiskResult]:

    company_dict = company.model_dump()

    raw = iso_analyze(
        company=company_dict,
        fund_id=fund_id,
        data_dir=data_dir,
    )

    profile = _build_profile(company)
    risk    = RiskResult(
        level=raw["level"],
        score=raw["score"],
        factors=raw["factors"],
        suggestions=raw["suggestions"],
        compared_to=raw["compared_to"],
    )
    return profile, risk
