"""
# ⚠️  주의: 이 스크립트를 재실행하면 fund_info.json 이 초기화됩니다.
#    apply_url / guide_url / apply_period / contact / checklist 필드는
#    스크립트 실행 후 data/processed/fund_info.json 에 수동으로 다시 추가하거나
#    별도 패치 스크립트(data/scripts/patch_fund_metadata.py)를 실행하세요.


FundPilot 데이터 전처리 스크립트
실행: python data/scripts/preprocess.py
출력: data/processed/ 에 JSON 4개 생성
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)


# ────────────────────────────────────────────────────────────
# 유틸
# ────────────────────────────────────────────────────────────

def read_csv(filename: str) -> pd.DataFrame:
    path = RAW / filename
    for enc in ["utf-8-sig", "cp949", "euc-kr"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    raise ValueError(f"인코딩 실패: {filename}")


def normalize(d: dict) -> dict:
    total = sum(d.values())
    if total == 0:
        return d
    return {k: round(v / total, 4) for k, v in d.items()}


def save(name: str, data):
    path = OUT / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {name} 저장 완료")


# ────────────────────────────────────────────────────────────
# 상수
# ────────────────────────────────────────────────────────────

INDUSTRIES = ["금속", "기계", "전기", "전자", "섬유", "화공", "잡화", "식료", "정보", "유통", "기타"]

AGE_BUCKETS   = ["1년미만", "3년미만", "5년미만", "7년미만", "10년미만", "15년미만", "20년미만", "20년이상"]
AGE_MIDPOINTS = [0.5, 2, 4, 6, 8.5, 12.5, 17.5, 25]

ASSET_BUCKETS_AGG = ["10억미만", "30억미만", "70억미만", "100억미만", "200억미만", "200억이상"]
ASSET_BUCKETS_REC = ["10억미만", "30억미만", "50억미만", "70억미만", "100억미만", "200억미만", "200억이상"]
ASSET_MID_REC     = [5, 20, 40, 60, 85, 150, 250]

INTEREST_RATES = {
    "창업기반지원":       2.84,
    "청년전용창업":       2.50,
    "개발기술사업화":     3.14,
    "혁신성장지원":       3.64,
    "제조현장스마트화":   3.14,
    "netzero":           3.64,
    "수출기업글로벌화":   3.14,
    "내수기업수출기업화": 3.14,
    "일시적경영애로":     3.64,
    "재해중소기업":       1.90,
    "사업전환":           3.14,
    "재창업":             3.14,
    "구조개선전용":       3.14,
    "사회적기업":         3.14,
    "소셜벤처":           3.14,
    "예비사회적기업":     3.14,
    "협동조합":           3.14,
    "마을기업":           3.14,
    "자활기업":           3.14,
}

FUND_META = {
    "창업기반지원":     {"display": "창업기반지원(일반)",  "category": "혁신창업사업화자금",  "special_type": None,            "purpose_hint": ["시설", "운전"]},
    "혁신성장지원":     {"display": "혁신성장지원",        "category": "신성장기반자금",       "special_type": None,            "purpose_hint": ["시설", "운전"]},
    "제조현장스마트화": {"display": "제조현장스마트화",    "category": "신성장기반자금",       "special_type": None,            "purpose_hint": ["시설"]},
    "netzero":         {"display": "Net-Zero 유망기업",   "category": "신성장기반자금",       "special_type": "ESG",           "purpose_hint": ["시설", "운전"]},
    "수출기업글로벌화": {"display": "수출기업 글로벌화",  "category": "신시장진출지원자금",   "special_type": "수출",           "purpose_hint": ["운전"]},
    "일시적경영애로":   {"display": "일시적경영애로",      "category": "긴급경영안정자금",     "special_type": None,            "purpose_hint": ["운전"]},
    "사회적기업":       {"display": "사회적기업",          "category": "사회적경제",           "special_type": "사회적기업",    "purpose_hint": ["시설", "운전"]},
    "소셜벤처":         {"display": "소셜벤처",            "category": "사회적경제",           "special_type": "소셜벤처",      "purpose_hint": ["시설", "운전"]},
    "예비사회적기업":   {"display": "예비사회적기업",      "category": "사회적경제",           "special_type": "예비사회적기업","purpose_hint": ["시설", "운전"]},
    "협동조합":         {"display": "협동조합",            "category": "사회적경제",           "special_type": "협동조합",      "purpose_hint": ["시설", "운전"]},
    "마을기업":         {"display": "마을기업",            "category": "사회적경제",           "special_type": "마을기업",      "purpose_hint": ["시설", "운전"]},
    "자활기업":         {"display": "자활기업",            "category": "사회적경제",           "special_type": "자활기업",      "purpose_hint": ["시설", "운전"]},
}

AGG_KEY_MAP = {
    "창업기반지원(일반)":     "창업기반지원",
    "혁신성장지원(일반)":     "혁신성장지원",
    "제조현장스마트화":       "제조현장스마트화",
    "Net-Zero 유망기업 지원": "netzero",
    "수출기업 글로벌화":      "수출기업글로벌화",
    "일시적경영애로":         "일시적경영애로",
}

STAT_KEY_MAP = {
    "창업기반지원(일반)":     "창업기반지원",
    "혁신성장지원(일반)":     "혁신성장지원",
    "제조현장스마트화":       "제조현장스마트화",
    "Net-Zero 유망기업 지원": "netzero",
    "수출기업 글로벌화":      "수출기업글로벌화",
    "일시적경영애로":         "일시적경영애로",
}

SCALE_KEY_MAP = {
    "창업기반지원":        "창업기반지원",
    "혁신성장지원자금":    "혁신성장지원",
    "제조현장스마트화":    "제조현장스마트화",
    "Net-Zero 유망기업 지원": "netzero",
    "수출기업글로벌화":    "수출기업글로벌화",
    "긴급경영안정자금":    "일시적경영애로",
}


# ────────────────────────────────────────────────────────────
# 1. exclusion_rules.json
# ────────────────────────────────────────────────────────────

def build_exclusion_rules():
    print("\n[1/4] 융자제외 업종 처리 중...")
    df = read_csv("중소벤처기업진흥공단_정책자금_융자제외_대상_업종_20260101.csv")
    rules = []
    for _, row in df.iterrows():
        rules.append({
            "category":      str(row["업종 분류"]).strip(),
            "industry_code": str(row["산업분류코드"]).strip(),
            "description":   str(row["융자 제외 업종"]).strip(),
        })

    cat_counts = {}
    for r in rules:
        cat_counts[r["category"]] = cat_counts.get(r["category"], 0) + 1

    save("exclusion_rules.json", {
        "base_date":   "2026-01-01",
        "total":       len(rules),
        "by_category": cat_counts,
        "rules":       rules,
    })
    print(f"     제외 업종 {len(rules)}개, 카테고리 {len(cat_counts)}개")


# ────────────────────────────────────────────────────────────
# 2. debt_limits.json
# ────────────────────────────────────────────────────────────

def build_debt_limits():
    print("\n[2/4] 업종별 부채비율 처리 중...")
    df = read_csv("중소벤처기업진흥공단_정책자금_업종별_융자제한_부채비율_20260101.csv")
    limits = []
    for _, row in df.iterrows():
        limits.append({
            "industry":                  str(row["업종"]).strip(),
            "avg_ratio":                 float(row["평균부채 비율"]),
            "limit_ratio":               float(row["제한부채 비율"]),
            "business_conversion_ratio": float(row["사업전환"]),
        })

    avg_vals   = [l["avg_ratio"] for l in limits]
    limit_vals = [l["limit_ratio"] for l in limits]

    save("debt_limits.json", {
        "base_date": "2026-01-01",
        "total":     len(limits),
        "summary": {
            "avg_of_avg_ratio": round(float(np.mean(avg_vals)), 1),
            "max_limit_ratio":  float(max(limit_vals)),
            "min_limit_ratio":  float(min(limit_vals)),
        },
        "limits": limits,
    })
    print(f"     업종 {len(limits)}개 부채비율 기준 저장")


# ────────────────────────────────────────────────────────────
# 3. fund_info.json
# ────────────────────────────────────────────────────────────

def build_fund_info():
    print("\n[3/4] 정책자금 기본정보 처리 중...")

    # 융자규모
    scale_df  = read_csv("중소벤처기업진흥공단_정책자금_융자규모_20260101.csv")
    scale_map = {str(r["자금명(중분류)"]).strip(): float(r["융자규모(억원)"]) for _, r in scale_df.iterrows()}

    # 자금종류별 융자현황
    stat_df  = read_csv("중소벤처기업진흥공단_정책자금_자금종류별_융자_현황_20251231.csv")
    stat_map = {}
    for _, row in stat_df.iterrows():
        name     = str(row["구분"]).strip()
        apply    = int(row["신청건수"])
        approved = int(row["지원결정건수"])
        loan_mil = float(row["대출금액(백만원)"])
        stat_map[name] = {
            "apply_count":    apply,
            "approved_count": approved,
            "approval_rate":  round(approved / apply * 100, 1) if apply > 0 else None,
            "loan_amount_mil": round(loan_mil, 0),
            "avg_loan_mil":    round(loan_mil / approved, 1) if approved > 0 else None,
        }

    # 업종별 지원현황 — 자금별 TOP3 업종
    ind_df  = read_csv("중소벤처기업진흥공단_정책자금_업종별_지원_현황_20251231.csv")
    ind_top = {}
    for _, row in ind_df.iterrows():
        name   = str(row["구분"]).strip()
        scores = {ind: float(row.get(f"{ind} 건수", 0)) for ind in INDUSTRIES}
        ind_top[name] = [k for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3] if v > 0]

    # 업력별 지원현황 — 자금별 주요 업력대
    age_df  = read_csv("중소벤처기업진흥공단_정책자금_업력별_지원현황_20251231.csv")
    age_top = {}
    for _, row in age_df.iterrows():
        name   = str(row["구분"]).strip()
        scores = {b: float(row.get(f"{b}건수(단위_개)", 0)) for b in AGE_BUCKETS}
        age_top[name] = [k for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2] if v > 0]

    # 자산규모별 지원현황 — 평균 자산 + 주요 구간
    asset_df  = read_csv("중소벤처기업진흥공단_정책자금_자산_규모별_지원현황_20251231.csv")
    asset_top = {}
    asset_col_map = {
        "10억미만":  ("10억미만 건수",  5),
        "30억미만":  ("30억미만 건수",  20),
        "70억미만":  ("70억미만 건수",  50),
        "100억미만": ("100억미만 건수", 85),
        "200억미만": ("200억미만 건수", 150),
        "200억이상": ("200억이상 건수", 250),
    }
    for _, row in asset_df.iterrows():
        name = str(row["구분"]).strip()
        scores, wsum, total = {}, 0.0, 0.0
        for label, (col, mid) in asset_col_map.items():
            cnt = float(row.get(col, 0))
            scores[label] = cnt
            wsum  += cnt * mid
            total += cnt
        asset_top[name] = {
            "top_buckets":    [k for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2] if v > 0],
            "avg_asset_bil":  round(wsum / total, 1) if total > 0 else None,
        }

    # 조립
    funds = []
    for key, meta in FUND_META.items():
        limit_amount = next(
            (v for k, v in scale_map.items() if any(sk in k for sk, fk in SCALE_KEY_MAP.items() if fk == key)),
            None
        )
        stat_name = next((k for k, v in STAT_KEY_MAP.items() if v == key), None)
        stats     = stat_map.get(stat_name, {})
        agg_name  = next((k for k, v in AGG_KEY_MAP.items() if v == key), None)

        funds.append({
            "id":            key,
            "display_name":  meta["display"],
            "category":      meta["category"],
            "special_type":  meta["special_type"],
            "purpose_hint":  meta["purpose_hint"],
            "interest_rate": INTEREST_RATES.get(key, 3.14),
            "limit_amount_bil":  limit_amount,
            "apply_count":       stats.get("apply_count"),
            "approved_count":    stats.get("approved_count"),
            "approval_rate":     stats.get("approval_rate"),
            "loan_amount_mil":   stats.get("loan_amount_mil"),
            "avg_loan_mil":      stats.get("avg_loan_mil"),
            "top_industries":    ind_top.get(agg_name, []),
            "top_age_buckets":   age_top.get(agg_name, []),
            "top_asset_buckets": asset_top.get(agg_name, {}).get("top_buckets", []),
            "avg_beneficiary_asset_bil": asset_top.get(agg_name, {}).get("avg_asset_bil"),
        })

    save("fund_info.json", {
        "base_rate":   3.14,
        "quarter":     "2026-Q2",
        "data_date":   "2025-12-31",
        "total_funds": len(funds),
        "funds":       funds,
    })
    print(f"     정책자금 {len(funds)}개 저장")


# ────────────────────────────────────────────────────────────
# 4. fund_patterns.json
# ────────────────────────────────────────────────────────────

def extract_from_records(df: pd.DataFrame, age_col: str, asset_col: str | None) -> dict:
    industry_dist = normalize(df["업종"].value_counts().to_dict())

    age_raw  = {str(k): int(v) for k, v in df[age_col].value_counts().items() if str(k) != "nan"}
    age_dist = normalize(age_raw)
    age_lbl  = dict(zip(AGE_BUCKETS, AGE_MIDPOINTS))
    avg_age  = round(sum(age_lbl.get(k, 10) * v for k, v in age_dist.items()), 2)

    if asset_col and asset_col in df.columns:
        asset_raw  = {str(k): int(v) for k, v in df[asset_col].value_counts().items() if str(k) != "nan"}
        asset_dist = normalize(asset_raw)
        asset_lbl  = dict(zip(ASSET_BUCKETS_REC, ASSET_MID_REC))
        avg_asset  = round(sum(asset_lbl.get(k, 50) * v for k, v in asset_dist.items()), 2)
    else:
        asset_dist, avg_asset = {}, None

    region_col  = next((c for c in ["지역구분(중진공)", "지역"] if c in df.columns), None)
    region_dist = normalize(df[region_col].value_counts().to_dict()) if region_col else {}

    f_cols = [c for c in df.columns if "시설" in c and any(x in c for x in ["신청", "대여", "공급"])]
    o_cols = [c for c in df.columns if "운전" in c and any(x in c for x in ["신청", "대여", "공급"])]
    if f_cols and o_cols:
        f_sum  = float(df[f_cols[0]].sum())
        o_sum  = float(df[o_cols[0]].sum())
        total  = f_sum + o_sum
        purpose_ratio = {"시설": round(f_sum / total, 4), "운전": round(o_sum / total, 4)} if total > 0 else {}
    else:
        purpose_ratio = {}

    amt_cols   = [c for c in df.columns if "대여금액" in c and "합계" in c] + \
                 [c for c in df.columns if "공급금액" in c and "합계" in c] + \
                 [c for c in df.columns if "대출금액" in c]
    avg_amount = round(float(df[amt_cols[0]].mean()), 1) if amt_cols else None
    max_amount = round(float(df[amt_cols[0]].max()), 1)  if amt_cols else None
    median_amt = round(float(df[amt_cols[0]].median()), 1) if amt_cols else None

    top_industries = [k for k, _ in sorted(industry_dist.items(), key=lambda x: x[1], reverse=True)[:3]]
    top_regions    = [k for k, _ in sorted(region_dist.items(),   key=lambda x: x[1], reverse=True)[:3]]

    return {
        "sample_count":    len(df),
        "industry_dist":   industry_dist,
        "age_dist":        age_dist,
        "asset_dist":      asset_dist,
        "region_dist":     region_dist,
        "purpose_ratio":   purpose_ratio,
        "top_industries":  top_industries,
        "top_regions":     top_regions,
        "avg_age_years":   avg_age,
        "avg_asset_bil":   avg_asset,
        "avg_amount_mil":  avg_amount,
        "max_amount_mil":  max_amount,
        "median_amount_mil": median_amt,
    }


def extract_from_simple(df: pd.DataFrame) -> dict:
    industry_dist = normalize(df["업종"].value_counts().to_dict())
    age_dist      = normalize({str(k): int(v) for k, v in df["업력"].value_counts().items()})
    region_dist   = normalize(df["지역"].value_counts().to_dict())

    age_lbl = dict(zip(AGE_BUCKETS, AGE_MIDPOINTS))
    avg_age = round(sum(age_lbl.get(k, 10) * v for k, v in age_dist.items()), 2)

    amt_col    = "대출금액(백만원)"
    avg_amount = round(float(df[amt_col].mean()), 1)   if amt_col in df.columns else None
    max_amount = round(float(df[amt_col].max()), 1)    if amt_col in df.columns else None
    median_amt = round(float(df[amt_col].median()), 1) if amt_col in df.columns else None

    top_industries = [k for k, _ in sorted(industry_dist.items(), key=lambda x: x[1], reverse=True)[:3]]
    top_regions    = [k for k, _ in sorted(region_dist.items(),   key=lambda x: x[1], reverse=True)[:3]]

    return {
        "sample_count":      len(df),
        "industry_dist":     industry_dist,
        "age_dist":          age_dist,
        "asset_dist":        {},
        "region_dist":       region_dist,
        "purpose_ratio":     {},
        "top_industries":    top_industries,
        "top_regions":       top_regions,
        "avg_age_years":     avg_age,
        "avg_asset_bil":     None,
        "avg_amount_mil":    avg_amount,
        "max_amount_mil":    max_amount,
        "median_amount_mil": median_amt,
    }


def build_feature_vector(pat: dict) -> list:
    """25차원 L2 정규화 벡터: 업종(11) + 업력(8) + 자산(6)"""
    ind_src   = pat.get("industry_dist_agg") or pat.get("industry_dist", {})
    age_src   = pat.get("age_dist_agg")      or pat.get("age_dist", {})
    asset_src = pat.get("asset_dist_agg")    or pat.get("asset_dist", {})

    vec = (
        [ind_src.get(ind, 0.0) for ind in INDUSTRIES] +
        [age_src.get(b, 0.0)   for b   in AGE_BUCKETS] +
        [asset_src.get(b, 0.0) for b   in ASSET_BUCKETS_AGG]
    )
    norm = float(np.linalg.norm(vec))
    return [round(v / norm, 6) for v in vec] if norm > 0 else vec


def build_fund_patterns():
    print("\n[4/4] 정책자금 표준 수혜 패턴 처리 중...")
    patterns: dict = {}

    detailed_files = [
        ("창업기반지원",    "중소벤처기업진흥공단_정책자금_창업기반지원_일반___지원_현황_20241231.csv",        "업력구분(중진공)", "자산규모"),
        ("일시적경영애로",  "중소벤처기업진흥공단_정책자금_일시적경영애로__지원_현황_20241231.csv",           "업력구분(중진공)", "자산규모"),
        ("혁신성장지원",    "중소벤처기업진흥공단_정책자금_이차보전_혁신성장지원__지원_현황_20251231.csv",     "업력구분(중진공)", "자산규모"),
        ("수출기업글로벌화","중소벤처기업진흥공단_정책자금_이차보전_수출기업_글로벌화__지원_현황_20251231.csv", "업력구분(중진공)", "자산규모"),
        ("제조현장스마트화","중소벤처기업진흥공단_정책자금_이차보전_제조현장스마트화__지원_현황_20251231.csv",  "업력구분(중진공)", "자산규모"),
        ("netzero",        "중소벤처기업진흥공단_정책자금_이차보전_Net_Zero_유망기업_지원__지원_현황_20251231.csv", "업력구분(중진공)", "자산규모"),
    ]
    for key, fname, age_col, asset_col in detailed_files:
        df = read_csv(fname)
        patterns[key] = extract_from_records(df, age_col=age_col, asset_col=asset_col)
        print(f"     {key}: {len(df)}건")

    simple_files = [
        ("사회적기업",     "중소벤처기업진흥공단_정책자금_사회적기업_지원_현황_20241231.csv"),
        ("소셜벤처",       "중소벤처기업진흥공단_정책자금_소셜벤처_지원_현황_20241231.csv"),
        ("예비사회적기업", "중소벤처기업진흥공단_정책자금_예비사회적기업_지원_현황_20241231.csv"),
        ("협동조합",       "중소벤처기업진흥공단_정책자금_협동조합_지원_현황_20241031.csv"),
        ("마을기업",       "중소벤처기업진흥공단_정책자금_마을기업_지원_현황_20240630.csv"),
        ("자활기업",       "중소벤처기업진흥공단_정책자금_자활기업_지원_현황_20241231.csv"),
    ]
    for key, fname in simple_files:
        df = read_csv(fname)
        patterns[key] = extract_from_simple(df)
        print(f"     {key}: {len(df)}건")

    # 집계 통계로 분포 보완
    ind_agg   = read_csv("중소벤처기업진흥공단_정책자금_업종별_지원_현황_20251231.csv")
    age_agg   = read_csv("중소벤처기업진흥공단_정책자금_업력별_지원현황_20251231.csv")
    asset_agg = read_csv("중소벤처기업진흥공단_정책자금_자산_규모별_지원현황_20251231.csv")

    for agg_name, key in AGG_KEY_MAP.items():
        row = ind_agg[ind_agg["구분"] == agg_name]
        if not row.empty:
            r = row.iloc[0]
            patterns[key]["industry_dist_agg"] = normalize({ind: float(r.get(f"{ind} 건수", 0)) for ind in INDUSTRIES})

        row = age_agg[age_agg["구분"] == agg_name]
        if not row.empty:
            r = row.iloc[0]
            patterns[key]["age_dist_agg"] = normalize({b: float(r.get(f"{b}건수(단위_개)", 0)) for b in AGE_BUCKETS})

        row = asset_agg[asset_agg["구분"] == agg_name]
        if not row.empty:
            r = row.iloc[0]
            col_map = {"10억미만": "10억미만 건수", "30억미만": "30억미만 건수", "70억미만": "70억미만 건수",
                       "100억미만": "100억미만 건수", "200억미만": "200억미만 건수", "200억이상": "200억이상 건수"}
            patterns[key]["asset_dist_agg"] = normalize({lb: float(r.get(col, 0)) for lb, col in col_map.items()})

    # 특성 벡터 + 메타 병합
    for key, pat in patterns.items():
        pat["feature_vector"] = build_feature_vector(pat)
        if key in FUND_META:
            pat.update({
                "display_name":  FUND_META[key]["display"],
                "category":      FUND_META[key]["category"],
                "special_type":  FUND_META[key]["special_type"],
                "interest_rate": INTEREST_RATES.get(key, 3.14),
            })

    save("fund_patterns.json", {
        "feature_dims":  25,
        "feature_order": {
            "0-10":  f"업종({', '.join(INDUSTRIES)})",
            "11-18": f"업력({', '.join(AGE_BUCKETS)})",
            "19-24": f"자산({', '.join(ASSET_BUCKETS_AGG)})",
        },
        "total_funds": len(patterns),
        "patterns":    patterns,
    })
    print(f"     {len(patterns)}개 자금 패턴 + 25차원 벡터 저장")


# ────────────────────────────────────────────────────────────
# 실행
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("FundPilot 데이터 전처리 시작")
    print("=" * 50)

    build_exclusion_rules()
    build_debt_limits()
    build_fund_info()
    build_fund_patterns()

    print("\n" + "=" * 50)
    print("완료. data/processed/ 확인:")
    for f in sorted(OUT.glob("*.json")):
        size = f.stat().st_size
        print(f"  {f.name:40s} {size:>8,} bytes")
    print("=" * 50)
