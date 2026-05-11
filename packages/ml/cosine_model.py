"""
Cosine Similarity 기반 정책자금 추천 모델
fund_patterns.json 의 feature_vector 와 입력 벡터 간 유사도 계산
"""

import json
import math
from pathlib import Path

_patterns: dict | None = None
_fund_info: dict | None = None

INDUSTRIES    = ["금속", "기계", "전기", "전자", "섬유", "화공", "잡화", "식료", "정보", "유통", "기타"]
AGE_BUCKETS   = ["1년미만", "3년미만", "5년미만", "7년미만", "10년미만", "15년미만", "20년미만", "20년이상"]
ASSET_BUCKETS = ["10억미만", "30억미만", "70억미만", "100억미만", "200억미만", "200억이상"]


def _load(data_dir: str = "data/processed"):
    global _patterns, _fund_info
    if _patterns is None:
        p = Path(data_dir)
        _patterns  = json.loads((p / "fund_patterns.json").read_text(encoding="utf-8"))["patterns"]
        _fund_info = {
            f["id"]: f
            for f in json.loads((p / "fund_info.json").read_text(encoding="utf-8"))["funds"]
        }


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na > 0 and nb > 0 else 0.0


def _feature_contributions(user_vec: list[float], fund_vec: list[float]) -> dict:
    groups = {
        "업종":   (0,  11),
        "업력":   (11, 19),
        "자산규모": (19, 25),
    }
    total_dot = sum(a * b for a, b in zip(user_vec, fund_vec))
    return {
        name: round(sum(user_vec[i] * fund_vec[i] for i in range(s, e)) / total_dot, 4)
        if total_dot > 0 else 0.0
        for name, (s, e) in groups.items()
    }


def _top_match_reasons(user_vec: list[float], pat: dict) -> list[str]:
    reasons = []

    user_ind_idx = user_vec[:11].index(max(user_vec[:11]))
    user_ind     = INDUSTRIES[user_ind_idx]
    if user_ind in pat.get("top_industries", []):
        reasons.append(f"수혜기업 다수 업종({user_ind})과 일치")

    user_age_idx = user_vec[11:19].index(max(user_vec[11:19]))
    user_age_lbl = AGE_BUCKETS[user_age_idx]
    age_dist     = pat.get("age_dist_agg") or pat.get("age_dist", {})
    if age_dist.get(user_age_lbl, 0) >= 0.20:
        reasons.append(f"업력 {user_age_lbl} 수혜 비중 높음 ({round(age_dist[user_age_lbl]*100)}%)")

    user_asset_idx = user_vec[19:].index(max(user_vec[19:]))
    user_asset_lbl = ASSET_BUCKETS[user_asset_idx]
    asset_dist     = pat.get("asset_dist_agg") or pat.get("asset_dist", {})
    if asset_dist.get(user_asset_lbl, 0) >= 0.20:
        reasons.append(f"자산 규모({user_asset_lbl}) 수혜 패턴 부합")

    if not reasons:
        reasons.append("복합 특성 기반 유사도 산출")
    return reasons


def recommend(
    user_vec: list[float],
    company: dict,
    eligibility: dict,
    top_n: int = 5,
    data_dir: str = "data/processed",
) -> list[dict]:
    _load(data_dir)

    purpose       = str(company.get("purpose", "시설+운전"))
    special_types = set(company.get("special_types", []))
    user_purposes = {"시설", "운전"} if "+" in purpose else {purpose}

    results = []
    for fund_id, pat in _patterns.items():
        fund_meta = _fund_info.get(fund_id, {})

        purpose_hint    = set(fund_meta.get("purpose_hint", ["시설", "운전"]))
        purpose_overlap = len(purpose_hint & user_purposes) / max(len(purpose_hint), 1)

        special_type    = fund_meta.get("special_type")
        special_bonus   = 0.05 if (special_type and special_type in special_types) else 0.0
        special_penalty = 0.10 if (special_type and special_type not in special_types) else 0.0

        fund_vec   = pat.get("feature_vector", [])
        similarity = _cosine(user_vec, fund_vec) if fund_vec else 0.0
        score      = similarity * (0.7 + 0.3 * purpose_overlap) + special_bonus - special_penalty
        score      = max(0.0, min(1.0, score))

        elig_status   = eligibility.get(fund_id, {})
        contributions = _feature_contributions(user_vec, fund_vec) if fund_vec else {}
        reasons       = _top_match_reasons(user_vec, pat)

        results.append({
            "fund_id":        fund_id,
            "display_name":   fund_meta.get("display_name", fund_id),
            "category":       fund_meta.get("category", ""),
            "special_type":   special_type,
            "score":          round(score, 4),
            "similarity":     round(similarity, 4),
            "interest_rate":  fund_meta.get("interest_rate"),
            "limit_amount_bil": fund_meta.get("limit_amount_bil"),
            "avg_loan_mil":   fund_meta.get("avg_loan_mil"),
            "approval_rate":  fund_meta.get("approval_rate"),
            "avg_beneficiary_asset_bil": fund_meta.get("avg_beneficiary_asset_bil"),
            "top_industries": pat.get("top_industries", []),
            "top_regions":    pat.get("top_regions", []),
            "avg_age_years":  pat.get("avg_age_years"),
            "purpose_ratio":  pat.get("purpose_ratio", {}),
            "eligibility":    elig_status.get("status", "unknown"),
            "eligibility_reasons": elig_status.get("reasons", []),
            "contributions":  contributions,
            "match_reasons":  reasons,
            # 공고·체크리스트
            "apply_url":    fund_meta.get("apply_url"),
            "guide_url":    fund_meta.get("guide_url"),
            "apply_period": fund_meta.get("apply_period"),
            "contact":      fund_meta.get("contact"),
            "checklist":    fund_meta.get("checklist", []),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]
