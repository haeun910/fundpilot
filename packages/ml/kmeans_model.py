"""
K-Means 기반 기업 유형 클러스터링
fund_patterns.json 의 수혜 분포를 기반으로 합성 학습 데이터를 생성 후 군집화.
실제 CSV가 없어도 동작 (processed JSON 만 필요).

6개 클러스터:
  0: 초기창업형    — 업력 3년 미만, 소규모 자산
  1: 성장형        — 업력 3~10년, 중간 자산
  2: 성숙제조형    — 제조업, 업력 10년+, 중대형 자산
  3: 유통서비스형  — 유통·IT·서비스 업종
  4: 소셜경제형    — 사회적경제 관련 자금 수혜 패턴
  5: 수출글로벌형  — 수출·글로벌화 수혜 패턴
"""

import json
import numpy as np
from pathlib import Path
from ml.preprocessor import INDUSTRIES, AGE_BUCKETS, ASSET_BUCKETS, soft_encode

_kmeans  = None
_scaler  = None
_trained = False

N_CLUSTERS = 6

CLUSTER_LABELS = {
    0: "초기창업형",
    1: "성장형",
    2: "성숙제조형",
    3: "유통서비스형",
    4: "소셜경제형",
    5: "수출글로벌형",
}

CLUSTER_DESC = {
    0: "창업 3년 이내 초기 기업으로 창업기반지원 자금에 적합한 유형",
    1: "업력 3~10년의 성장기 기업으로 혁신성장·스마트화 자금 수혜 비중이 높은 유형",
    2: "업력 10년 이상 제조업 중심의 성숙 기업으로 대규모 시설자금 수요가 높은 유형",
    3: "유통·IT·서비스업 중심으로 운전자금 및 디지털 전환 관련 자금 수요가 높은 유형",
    4: "사회적기업·협동조합 등 사회적경제 조직에 특화된 지원 패턴",
    5: "수출 실적 보유 또는 글로벌 진출을 추진하는 기업으로 수출 특화 자금에 적합한 유형",
}


# ── 합성 학습 데이터 생성 ────────────────────────────────────────

AGE_MID    = [0.5, 2, 4, 6, 8.5, 12.5, 17.5, 25]
ASSET_MID  = [5, 20, 60, 85, 150, 250]


def _make_vec(ind_idx: int, age_idx: int, asset_idx: int) -> np.ndarray:
    """preprocessor.vectorize 와 동일한 25차원 벡터 생성"""
    v_ind   = [1.0 if i == ind_idx else 0.0 for i in range(len(INDUSTRIES))]
    v_age   = soft_encode(age_idx,   len(AGE_BUCKETS),   spread=1.2)
    v_asset = soft_encode(asset_idx, len(ASSET_BUCKETS), spread=1.2)
    vec  = v_ind + v_age + v_asset
    norm = float(np.linalg.norm(vec))
    return np.array([v / norm for v in vec] if norm > 0 else vec)


def _sample_from_dist(dist: dict, keys: list, n: int, rng: np.random.Generator) -> list[int]:
    """분포 딕셔너리에서 n개 인덱스 샘플링"""
    probs = [max(dist.get(k, 0), 0) for k in keys]
    total = sum(probs)
    if total == 0:
        probs = [1.0 / len(keys)] * len(keys)
    else:
        probs = [p / total for p in probs]
    return rng.choice(len(keys), size=n, p=probs).tolist()


def _build_training_data(data_dir: str) -> np.ndarray:
    """fund_patterns.json 분포 → 합성 학습 벡터 생성"""
    p = Path(data_dir)
    patterns = json.loads((p / "fund_patterns.json").read_text(encoding="utf-8"))["patterns"]

    rng   = np.random.default_rng(42)
    rows  = []
    N_PER_FUND = 300  # 자금별 합성 샘플 수

    for fund_id, pat in patterns.items():
        ind_dist   = pat.get("industry_dist_agg") or pat.get("industry_dist", {})
        age_dist   = pat.get("age_dist_agg")       or pat.get("age_dist", {})
        asset_dist = pat.get("asset_dist_agg")     or pat.get("asset_dist", {})

        ind_samples   = _sample_from_dist(ind_dist,   INDUSTRIES,   N_PER_FUND, rng)
        age_samples   = _sample_from_dist(age_dist,   AGE_BUCKETS,  N_PER_FUND, rng)
        asset_samples = _sample_from_dist(asset_dist, ASSET_BUCKETS, N_PER_FUND, rng)

        for ind_i, age_i, asset_i in zip(ind_samples, age_samples, asset_samples):
            rows.append(_make_vec(ind_i, age_i, asset_i))

    return np.array(rows, dtype=float)


# ── 학습 ─────────────────────────────────────────────────────────

def train(data_dir: str = "data/processed"):
    global _kmeans, _scaler, _trained

    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        raise ImportError("scikit-learn 설치 필요: pip install scikit-learn")

    X = _build_training_data(data_dir)

    _scaler = StandardScaler()
    X_scaled = _scaler.fit_transform(X)

    _kmeans = KMeans(
        n_clusters=N_CLUSTERS,
        random_state=42,
        n_init=20,
        max_iter=500,
    )
    _kmeans.fit(X_scaled)
    _trained = True


def _ensure_trained(data_dir: str):
    if not _trained:
        train(data_dir)


# ── 추론 ─────────────────────────────────────────────────────────

def predict(
    user_vec: list[float],
    data_dir: str = "data/processed",
) -> dict:
    """
    Parameters
    ----------
    user_vec : preprocessor.vectorize() 반환 25차원 벡터

    Returns
    -------
    {
        "cluster_id":    int,
        "cluster_label": str,   # "성장형" 등
        "cluster_desc":  str,
        "distance":      float, # 클러스터 중심까지 정규화 거리 (0~1, 낮을수록 전형적)
    }
    """
    _ensure_trained(data_dir)

    X = np.array([user_vec], dtype=float)
    X_scaled = _scaler.transform(X)

    cluster_id = int(_kmeans.predict(X_scaled)[0])

    # 클러스터 중심까지 거리 계산 (정규화)
    center     = _kmeans.cluster_centers_[cluster_id]
    dist_raw   = float(np.linalg.norm(X_scaled[0] - center))
    # 전체 클러스터 중심 간 평균 거리로 정규화
    all_dists  = [
        np.linalg.norm(_kmeans.cluster_centers_[i] - _kmeans.cluster_centers_[j])
        for i in range(N_CLUSTERS) for j in range(i + 1, N_CLUSTERS)
    ]
    avg_inter  = float(np.mean(all_dists)) if all_dists else 1.0
    dist_norm  = min(1.0, dist_raw / avg_inter) if avg_inter > 0 else 0.5

    return {
        "cluster_id":    cluster_id,
        "cluster_label": CLUSTER_LABELS.get(cluster_id, f"유형{cluster_id}"),
        "cluster_desc":  CLUSTER_DESC.get(cluster_id, ""),
        "distance":      round(dist_norm, 4),
    }
