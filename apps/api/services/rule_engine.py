"""
Rule-Based Engine
융자제외 업종 + 업종별 부채비율 기준으로 신청 가능 여부 판별
"""

import json
import re
from pathlib import Path

_exclusion_rules: list | None = None
_debt_limits: list | None     = None

FUND_IDS = [
    "창업기반지원", "혁신성장지원", "제조현장스마트화", "netzero",
    "수출기업글로벌화", "일시적경영애로",
    "사회적기업", "소셜벤처", "예비사회적기업", "협동조합", "마을기업", "자활기업",
]

# 특수유형 자금은 해당 유형 기업만 신청 가능
SPECIAL_TYPE_FUNDS = {
    "사회적기업":    "사회적기업",
    "소셜벤처":      "소셜벤처",
    "예비사회적기업": "예비사회적기업",
    "협동조합":      "협동조합",
    "마을기업":      "마을기업",
    "자활기업":      "자활기업",
    "netzero":      "ESG",
    "수출기업글로벌화": "수출",
}

# 용도 매핑: 자금별로 지원 가능한 용도
FUND_PURPOSE_MAP = {
    "창업기반지원":     ["시설", "운전"],
    "혁신성장지원":     ["시설", "운전"],
    "제조현장스마트화": ["시설"],
    "netzero":         ["시설", "운전"],
    "수출기업글로벌화": ["운전"],
    "일시적경영애로":   ["운전"],
    "사회적기업":       ["시설", "운전"],
    "소셜벤처":         ["시설", "운전"],
    "예비사회적기업":   ["시설", "운전"],
    "협동조합":         ["시설", "운전"],
    "마을기업":         ["시설", "운전"],
    "자활기업":         ["시설", "운전"],
}


def _load(data_dir: str = "data/processed"):
    global _exclusion_rules, _debt_limits
    if _exclusion_rules is None:
        p = Path(data_dir)
        _exclusion_rules = json.loads(
            (p / "exclusion_rules.json").read_text(encoding="utf-8")
        )["rules"]
        _debt_limits = json.loads(
            (p / "debt_limits.json").read_text(encoding="utf-8")
        )["limits"]


def _is_excluded_industry(industry: str) -> tuple[bool, str | None]:
    """
    Returns (is_excluded, reason)
    업종 키워드로 제외 목록 검색 (부분 일치)
    """
    industry_lower = industry.lower()
    for rule in _exclusion_rules:
        desc = rule["description"].lower()
        cat  = rule["category"].lower()
        # 카테고리 또는 설명에 키워드 포함 여부
        if any(kw in industry_lower for kw in desc.split()[:3]):
            return True, f"융자제외 업종: {rule['description']}"
        # 특정 고위험 카테고리 직접 체크
        if "부동산" in industry and "부동산" in cat:
            return True, "융자제외 업종: 부동산업"
        if "금융" in industry and "금융" in cat:
            return True, "융자제외 업종: 금융 및 보험업"
    return False, None


def _find_debt_limit(industry: str) -> dict | None:
    """
    업종명으로 부채비율 제한 검색
    KIS 코드 또는 한글 업종명 부분 매칭
    """
    for limit in _debt_limits:
        ind_str = limit["industry"]
        # 한글 업종명 추출 (괄호 안)
        match = re.search(r'\(([^)]+)\)', ind_str)
        kor_name = match.group(1) if match else ind_str

        if kor_name in industry or industry in kor_name:
            return limit
        # 주요 키워드 매핑
        keyword_map = {
            "제조": "C(제조업)", "건설": "F(건설업)", "도매": "G(도매 및 소매업)",
            "소매": "G(도매 및 소매업)", "유통": "G(도매 및 소매업)",
            "운수": "H(운수 및 창고업)", "물류": "H(운수 및 창고업)",
            "정보": "J(정보통신업)", "IT": "J(정보통신업)",
            "부동산": "L(부동산업)",
        }
        for kw, target in keyword_map.items():
            if kw in industry and target in ind_str:
                return limit

    # 기본값: 제조업 기준 적용
    for limit in _debt_limits:
        if "C(제조업)" == limit["industry"]:
            return limit
    return None


def check(company: dict, data_dir: str = "data/processed") -> dict:
    """
    Parameters
    ----------
    company : {
        industry     (str)  : 업종
        debt_ratio   (float): 부채비율 (%)
        purpose      (str)  : '시설' | '운전' | '시설+운전'
        special_types (list): ['사회적기업', '소셜벤처', ...]
        age_years    (float): 업력
    }

    Returns
    -------
    {
        "overall": "가능" | "조건부" | "제한",
        "reasons": [...],
        "by_fund": {
            fund_id: {
                "status":  "가능" | "조건부" | "제한",
                "reasons": [...],
            }
        }
    }
    """
    _load(data_dir)

    industry      = str(company.get("industry", ""))
    debt_ratio    = float(company.get("debt_ratio", 0))
    purpose       = str(company.get("purpose", "시설+운전"))
    special_types = set(company.get("special_types", []))
    age_years     = float(company.get("age_years", 5))

    overall_reasons: list[str] = []
    overall_status  = "가능"

    # ── 1. 융자제외 업종 확인 ─────────────────────────────────
    is_excluded, exc_reason = _is_excluded_industry(industry)
    if is_excluded:
        overall_reasons.append(exc_reason)
        overall_status = "제한"

    # ── 2. 부채비율 확인 ─────────────────────────────────────
    debt_limit_info = _find_debt_limit(industry)
    debt_status     = "가능"
    if debt_limit_info:
        limit = debt_limit_info["limit_ratio"]
        avg   = debt_limit_info["avg_ratio"]
        if debt_ratio > limit:
            overall_reasons.append(
                f"부채비율 {debt_ratio:.0f}% > 제한 기준 {limit:.0f}% (업종 평균 {avg:.0f}%)"
            )
            overall_status = "제한"
            debt_status    = "제한"
        elif debt_ratio > limit * 0.8:
            overall_reasons.append(
                f"부채비율 {debt_ratio:.0f}% — 제한 기준({limit:.0f}%) 80% 근접"
            )
            if overall_status == "가능":
                overall_status = "조건부"
            debt_status = "조건부"

    # ── 3. 자금별 개별 판정 ──────────────────────────────────
    by_fund: dict = {}

    for fund_id in FUND_IDS:
        fund_reasons: list[str] = []
        fund_status  = "가능"

        # 전체 제한이면 그대로 전파
        if overall_status == "제한":
            fund_status = "제한"
            fund_reasons = overall_reasons.copy()
        else:
            # 부채비율 조건부 전파
            if debt_status in ("조건부", "제한"):
                fund_status = debt_status
                if overall_reasons:
                    fund_reasons += overall_reasons

        # 특수유형 자금 접근 조건
        required_type = SPECIAL_TYPE_FUNDS.get(fund_id)
        if required_type:
            if required_type not in special_types:
                fund_status  = "제한"
                fund_reasons.append(f"{required_type} 인증/해당 기업만 신청 가능")

        # 용도 불일치
        fund_purposes = FUND_PURPOSE_MAP.get(fund_id, ["시설", "운전"])
        user_purposes = {"시설", "운전"} if "+" in purpose else {purpose}
        if not any(p in fund_purposes for p in user_purposes):
            if fund_status == "가능":
                fund_status = "조건부"
            fund_reasons.append(
                f"용도 불일치: 해당 자금은 {'/'.join(fund_purposes)} 전용"
            )

        # 업력 조건 (창업기반지원: 7년 미만)
        if fund_id == "창업기반지원" and age_years >= 7:
            fund_status  = "제한"
            fund_reasons.append(f"창업기반지원: 업력 7년 미만 기업 대상 (현재 {age_years:.1f}년)")

        # 재창업 케이스는 별도이므로 스킵

        if not fund_reasons:
            fund_reasons.append("신청 조건 충족")

        by_fund[fund_id] = {
            "status":  fund_status,
            "reasons": fund_reasons,
        }

    if not overall_reasons:
        overall_reasons.append("주요 신청 제한 조건 미해당")

    return {
        "overall":  overall_status,
        "reasons":  overall_reasons,
        "by_fund":  by_fund,
        "debt_limit_info": {
            "industry":    debt_limit_info["industry"] if debt_limit_info else None,
            "avg_ratio":   debt_limit_info["avg_ratio"] if debt_limit_info else None,
            "limit_ratio": debt_limit_info["limit_ratio"] if debt_limit_info else None,
        } if debt_limit_info else None,
    }
