"""
추천 오케스트레이터
rule_engine → preprocessor → kmeans_model → cosine_model 을 조합하여 최종 결과 반환
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[4] / "packages"))

from ml.preprocessor  import vectorize, get_industry_label, get_age_label, get_asset_label
from ml.cosine_model  import recommend as cosine_recommend
from ml.kmeans_model  import predict as kmeans_predict
from apps.api.services.rule_engine import check as rule_check
from apps.api.schemas.models import (
    CompanyInput, CompanyProfile, ClusterInfo,
    FundEligibility, EligibilityResult, DebtLimitInfo,
    FundRecommendation, ContributionInfo, ChecklistCategory,
)


def _build_profile(company: CompanyInput, user_vec: list[float], data_dir: str) -> CompanyProfile:
    cluster_raw = kmeans_predict(user_vec, data_dir=data_dir)
    return CompanyProfile(
        industry_category=get_industry_label(company.industry),
        age_label=get_age_label(company.age_years),
        asset_label=get_asset_label(company.asset_bil),
        cluster=ClusterInfo(
            cluster_id=cluster_raw["cluster_id"],
            cluster_label=cluster_raw["cluster_label"],
            cluster_desc=cluster_raw["cluster_desc"],
            distance=cluster_raw["distance"],
        ),
    )


def _build_eligibility(raw: dict) -> FundEligibility:
    by_fund = {
        fid: EligibilityResult(status=v["status"], reasons=v["reasons"])
        for fid, v in raw["by_fund"].items()
    }
    dli = raw.get("debt_limit_info")
    return FundEligibility(
        overall=raw["overall"],
        reasons=raw["reasons"],
        by_fund=by_fund,
        debt_limit_info=DebtLimitInfo(**dli) if dli else None,
    )


def run(
    company: CompanyInput,
    top_n: int = 5,
    data_dir: str = "data/processed",
) -> tuple[CompanyProfile, FundEligibility, list[FundRecommendation]]:

    company_dict = company.model_dump()

    # 1. Rule Engine — 신청 가능 여부 판별
    elig_raw    = rule_check(company_dict, data_dir=data_dir)
    eligibility = _build_eligibility(elig_raw)

    # 2. 벡터화 (25차원)
    user_vec = vectorize(company_dict)

    # 3. K-Means — 기업 유형 클러스터링
    profile = _build_profile(company, user_vec, data_dir=data_dir)

    # 4. Cosine Similarity — 정책자금 유사도 추천
    raw_recs = cosine_recommend(
        user_vec=user_vec,
        company=company_dict,
        eligibility=elig_raw["by_fund"],
        top_n=top_n,
        data_dir=data_dir,
    )

    # 5. 스키마 변환
    recommendations = []
    for rank, r in enumerate(raw_recs, 1):
        contrib_raw = r.get("contributions", {})
        raw_checklist = r.get("checklist", [])
        checklist = [
            ChecklistCategory(category=cat["category"], items=cat["items"])
            for cat in raw_checklist
        ]
        recommendations.append(FundRecommendation(
            fund_id=r["fund_id"],
            display_name=r["display_name"],
            category=r["category"],
            special_type=r.get("special_type"),
            rank=rank,
            score=r["score"],
            similarity=r["similarity"],
            eligibility=r["eligibility"],
            eligibility_reasons=r.get("eligibility_reasons", []),
            interest_rate=r.get("interest_rate"),
            limit_amount_bil=r.get("limit_amount_bil"),
            avg_loan_mil=r.get("avg_loan_mil"),
            approval_rate=r.get("approval_rate"),
            avg_beneficiary_asset_bil=r.get("avg_beneficiary_asset_bil"),
            top_industries=r.get("top_industries", []),
            top_regions=r.get("top_regions", []),
            avg_age_years=r.get("avg_age_years"),
            purpose_ratio=r.get("purpose_ratio", {}),
            contributions=ContributionInfo(
                업종=contrib_raw.get("업종", 0.0),
                업력=contrib_raw.get("업력", 0.0),
                자산규모=contrib_raw.get("자산규모", 0.0),
            ),
            match_reasons=r.get("match_reasons", []),
            apply_url=r.get("apply_url"),
            guide_url=r.get("guide_url"),
            apply_period=r.get("apply_period"),
            contact=r.get("contact"),
            checklist=checklist,
        ))

    return profile, eligibility, recommendations
