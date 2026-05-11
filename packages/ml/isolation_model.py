"""
Isolation Forest 기반 수혜 패턴 이탈 리스크 분석
학습 데이터: 개별 건별 수혜 기업 CSV (업력, 자산, 대출금액)
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

_model   = None
_scaler  = None
_trained = False
_stats   = {}   # 펀드별 수혜기업 평균 통계
_score_min: float = -1.0
_score_max: float =  0.0


# ── 학습 데이터 로드 ─────────────────────────────────────────

AGE_TO_MID = {
    "1년미만": 0.5, "3년미만": 2.0, "5년미만": 4.0, "7년미만": 6.0,
    "10년미만": 8.5, "15년미만": 12.5, "20년미만": 17.5, "20년이상": 25.0,
}
ASSET_TO_MID = {
    "10억미만": 5.0, "30억미만": 20.0, "50억미만": 40.0,
    "70억미만": 60.0, "100억미만": 85.0, "200억미만": 150.0, "200억이상": 250.0,
}


def _encode_row(row: pd.Series, age_col: str, asset_col: str | None) -> list[float] | None:
    age_mid = AGE_TO_MID.get(str(row.get(age_col, "")), None)
    if age_mid is None:
        return None

    asset_mid = None
    if asset_col and asset_col in row.index:
        asset_mid = ASSET_TO_MID.get(str(row.get(asset_col, "")), None)

    amt_cols = [c for c in row.index if "합계" in c and any(x in c for x in ["대여금액", "공급금액", "대출금액"])]
    amount   = float(row[amt_cols[0]]) if amt_cols else 0.0

    if asset_mid is not None:
        return [age_mid, asset_mid, amount]
    else:
        return [age_mid, amount]


def _load_training_data(data_dir: str) -> np.ndarray:
    """개별 건별 CSV → 학습용 numpy array"""
    raw = Path(data_dir).parent / "raw"
    files = [
        ("중소벤처기업진흥공단_정책자금_창업기반지원_일반___지원_현황_20241231.csv",        "업력구분(중진공)", "자산규모"),
        ("중소벤처기업진흥공단_정책자금_일시적경영애로__지원_현황_20241231.csv",           "업력구분(중진공)", "자산규모"),
        ("중소벤처기업진흥공단_정책자금_이차보전_혁신성장지원__지원_현황_20251231.csv",     "업력구분(중진공)", "자산규모"),
        ("중소벤처기업진흥공단_정책자금_이차보전_수출기업_글로벌화__지원_현황_20251231.csv", "업력구분(중진공)", "자산규모"),
        ("중소벤처기업진흥공단_정책자금_이차보전_제조현장스마트화__지원_현황_20251231.csv",  "업력구분(중진공)", "자산규모"),
        ("중소벤처기업진흥공단_정책자금_이차보전_Net_Zero_유망기업_지원__지원_현황_20251231.csv", "업력구분(중진공)", "자산규모"),
    ]
    rows = []
    for fname, age_col, asset_col in files:
        fpath = raw / fname
        if not fpath.exists():
            continue
        for enc in ["utf-8-sig", "cp949"]:
            try:
                df = pd.read_csv(fpath, encoding=enc)
                break
            except Exception:
                continue
        for _, row in df.iterrows():
            enc_row = _encode_row(row, age_col, asset_col)
            if enc_row and len(enc_row) == 3:
                rows.append(enc_row)

    return np.array(rows, dtype=float) if rows else np.zeros((10, 3))


def _compute_stats(data_dir: str):
    """펀드별 수혜기업 평균 통계 계산"""
    global _stats
    processed = Path(data_dir)
    patterns  = json.loads((processed / "fund_patterns.json").read_text(encoding="utf-8"))["patterns"]

    for fund_id, pat in patterns.items():
        age_dist   = pat.get("age_dist_agg") or pat.get("age_dist", {})
        asset_dist = pat.get("asset_dist_agg") or pat.get("asset_dist", {})

        avg_age   = sum(AGE_TO_MID.get(k, 10) * v for k, v in age_dist.items())
        avg_asset = sum(ASSET_TO_MID.get(k, 50) * v for k, v in asset_dist.items()) if asset_dist else None
        avg_amt   = pat.get("avg_amount_mil", 0) or 0

        _stats[fund_id] = {
            "avg_age":   round(avg_age, 2),
            "avg_asset": round(avg_asset, 2) if avg_asset else None,
            "avg_amount": avg_amt,
            "top_industries": pat.get("top_industries", []),
            "top_regions":    pat.get("top_regions", []),
        }


def train(data_dir: str = "data/processed"):
    """Isolation Forest 학습"""
    global _model, _scaler, _trained, _score_min, _score_max

    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        raise ImportError("scikit-learn 설치 필요: pip install scikit-learn")

    _compute_stats(data_dir)
    X = _load_training_data(data_dir)

    _scaler = StandardScaler()
    X_scaled = _scaler.fit_transform(X)

    _model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    _model.fit(X_scaled)

    # 학습 데이터 기준 실제 점수 범위를 저장해 정규화에 사용
    train_scores = _model.score_samples(X_scaled)
    _score_min = float(train_scores.min())
    _score_max = float(train_scores.max())

    _trained = True


def _ensure_trained(data_dir: str):
    if not _trained:
        train(data_dir)


def _normalize_score(raw_score: float) -> float:
    """
    score_samples 값을 0~1 범위로 정규화.
    학습 데이터 기준 min/max를 사용하여 상수에 의존하지 않음.
    반환값이 높을수록 이상치(리스크 높음).
    """
    span = _score_max - _score_min
    if span == 0:
        return 0.5
    # score_samples는 낮을수록 이상치 → 반전
    norm = (_score_max - raw_score) / span
    return max(0.0, min(1.0, norm))


def analyze(
    company: dict,
    fund_id: str | None = None,
    data_dir: str = "data/processed",
) -> dict:
    """
    Parameters
    ----------
    company  : 사용자 입력 (age_years, asset_bil, debt_ratio, industry, region)
    fund_id  : 특정 자금 기준 분석 (None이면 전체 평균 기준)

    Returns
    -------
    {
        "level": "낮음" | "보통" | "높음",
        "score": float,          # 0(정상) ~ 1(이상), 높을수록 위험
        "factors": [...],
        "suggestions": [...],
        "compared_to": {...}
    }
    """
    _ensure_trained(data_dir)

    age_years  = float(company.get("age_years", 5))
    asset_bil  = float(company.get("asset_bil", 30))
    debt_ratio = float(company.get("debt_ratio", 100))

    X_user   = np.array([[age_years, asset_bil, 0.0]])
    X_scaled = _scaler.transform(X_user)

    raw_score  = float(_model.score_samples(X_scaled)[0])
    norm_score = _normalize_score(raw_score)

    if norm_score < 0.3:
        level = "낮음"
    elif norm_score < 0.65:
        level = "보통"
    else:
        level = "높음"

    ref_stats = _stats.get(fund_id) if fund_id else None
    if ref_stats is None and _stats:
        ref_stats = {
            "avg_age":   float(np.mean([s["avg_age"] for s in _stats.values()])),
            "avg_asset": float(np.mean([s["avg_asset"] for s in _stats.values() if s["avg_asset"]])),
            "avg_amount": float(np.mean([s["avg_amount"] for s in _stats.values()])),
        }

    factors     = []
    suggestions = []

    if ref_stats:
        avg_age = ref_stats.get("avg_age", 5)
        if age_years < avg_age * 0.5:
            factors.append(f"업력이 평균 수혜기업({avg_age:.1f}년)보다 짧음")
            suggestions.append("창업기반지원 등 초기 창업형 자금 우선 검토 권장")
        elif age_years > avg_age * 2.5:
            factors.append(f"업력이 평균 수혜기업({avg_age:.1f}년)보다 현저히 긺")
            suggestions.append("성장·안정형 자금(혁신성장지원 등) 병행 검토")

        avg_asset = ref_stats.get("avg_asset") or 50
        if asset_bil < avg_asset * 0.3:
            factors.append(f"자산 규모가 평균 수혜기업({avg_asset:.0f}억)보다 작음")
        elif asset_bil > avg_asset * 3.0:
            factors.append(f"자산 규모가 평균 수혜기업({avg_asset:.0f}억)을 크게 초과")
            suggestions.append("스케일업금융 등 중견기업 대상 자금 검토")

    if debt_ratio > 400:
        factors.append(f"부채비율 {debt_ratio:.0f}% — 대부분 업종 제한 기준 초과 위험")
        suggestions.append("부채비율 개선 후 신청하거나 사업전환 자금 검토")
    elif debt_ratio > 200:
        factors.append(f"부채비율 {debt_ratio:.0f}% — 일부 업종 제한 기준 근접")
        suggestions.append("업종별 부채비율 제한 기준 재확인 권장")

    if not factors:
        factors.append("수혜 패턴과 전반적으로 유사한 기업 프로필")

    compared_to = {}
    if ref_stats:
        compared_to = {
            "avg_age_years":  ref_stats.get("avg_age"),
            "avg_asset_bil":  ref_stats.get("avg_asset"),
            "user_age_years": age_years,
            "user_asset_bil": asset_bil,
            "user_debt_ratio": debt_ratio,
        }

    return {
        "level":       level,
        "score":       round(norm_score, 4),
        "factors":     factors,
        "suggestions": suggestions if suggestions else ["현재 조건으로 신청 진행 가능"],
        "compared_to": compared_to,
    }
