"""
사용자 입력값 → 25차원 특성 벡터 변환
fund_patterns.json 의 feature_vector 와 동일한 공간으로 매핑
"""

import numpy as np

# ── 카테고리 정의 ──────────────────────────────────────────
INDUSTRIES = ["금속", "기계", "전기", "전자", "섬유", "화공", "잡화", "식료", "정보", "유통", "기타"]

AGE_BUCKETS   = ["1년미만", "3년미만", "5년미만", "7년미만", "10년미만", "15년미만", "20년미만", "20년이상"]
AGE_EDGES     = [0, 1, 3, 5, 7, 10, 15, 20, 999]   # 구간 경계

ASSET_BUCKETS = ["10억미만", "30억미만", "70억미만", "100억미만", "200억미만", "200억이상"]
ASSET_EDGES   = [0, 10, 30, 70, 100, 200, 9999]     # 억원 단위

# 업종 키워드 → 11개 카테고리 매핑
INDUSTRY_KEYWORD_MAP: dict[str, str] = {
    # 금속
    "금속": "금속", "철강": "금속", "비철": "금속", "주물": "금속", "단조": "금속",
    # 기계
    "기계": "기계", "장비": "기계", "자동차": "기계", "부품": "기계", "조선": "기계",
    "항공": "기계", "로봇": "기계",
    # 전기
    "전기": "전기", "전력": "전기", "발전": "전기", "배전": "전기",
    # 전자
    "전자": "전자", "반도체": "전자", "디스플레이": "전자", "통신장비": "전자",
    "가전": "전자", "PCB": "전자",
    # 섬유
    "섬유": "섬유", "의류": "섬유", "패션": "섬유", "봉제": "섬유", "신발": "섬유",
    # 화공
    "화학": "화공", "석유": "화공", "플라스틱": "화공", "고무": "화공",
    "의약": "화공", "화장품": "화공", "도료": "화공",
    # 잡화
    "가구": "잡화", "생활용품": "잡화", "완구": "잡화", "스포츠": "잡화",
    "인쇄": "잡화", "포장": "잡화",
    # 식료
    "식품": "식료", "음료": "식료", "식료": "식료", "농업": "식료",
    "수산": "식료", "제과": "식료",
    # 정보
    "정보": "정보", "소프트웨어": "정보", "IT": "정보", "콘텐츠": "정보",
    "게임": "정보", "앱": "정보", "플랫폼": "정보", "AI": "정보",
    # 유통
    "유통": "유통", "도매": "유통", "소매": "유통", "물류": "유통",
    "무역": "유통", "수출": "유통",
    # 기타
    "서비스": "기타", "교육": "기타", "의료": "기타", "건설": "기타",
    "관광": "기타", "음식": "기타", "숙박": "기타",
}


def map_industry(raw: str) -> str:
    """사용자 입력 업종 문자열 → 11개 카테고리 중 하나"""
    for keyword, category in INDUSTRY_KEYWORD_MAP.items():
        if keyword in raw:
            return category
    return "기타"


def age_to_bucket(years: float) -> int:
    """업력(년) → 업력 구간 인덱스"""
    for i, edge in enumerate(AGE_EDGES[1:]):
        if years < edge:
            return i
    return len(AGE_BUCKETS) - 1


def asset_to_bucket(asset_bil: float) -> int:
    """자산(억원) → 자산 구간 인덱스"""
    for i, edge in enumerate(ASSET_EDGES[1:]):
        if asset_bil < edge:
            return i
    return len(ASSET_BUCKETS) - 1


def soft_encode(idx: int, total: int, spread: float = 0.8) -> list[float]:
    """
    단순 one-hot 대신 인접 구간에 가중치 분산 (삼각 커널)
    → 경계값 근처 기업도 자연스럽게 매핑
    """
    vec = [0.0] * total
    for i in range(total):
        dist = abs(i - idx)
        val  = max(0.0, 1.0 - dist / spread)
        vec[i] = val
    total_w = sum(vec)
    return [v / total_w for v in vec] if total_w > 0 else vec


def vectorize(company: dict) -> list[float]:
    """
    company 딕셔너리 → 25차원 특성 벡터 (L2 정규화)

    company 필수 키:
        industry    (str)  : 업종 (자유 텍스트 or 11개 카테고리)
        age_years   (float): 업력 (년)
        asset_bil   (float): 자산 규모 (억원)

    company 선택 키:
        region      (str)  : 지역
        purpose     (str)  : '시설' | '운전' | '시설+운전'
        debt_ratio  (float): 부채비율 (%)
        employee_count (int): 종업원 수
    """
    industry = map_industry(str(company.get("industry", "")))
    age_idx  = age_to_bucket(float(company.get("age_years", 3)))
    asset_idx = asset_to_bucket(float(company.get("asset_bil", 20)))

    # 업종 one-hot (11차원)
    vec_ind  = [1.0 if ind == industry else 0.0 for ind in INDUSTRIES]
    # 업력 soft (8차원)
    vec_age  = soft_encode(age_idx,   len(AGE_BUCKETS),   spread=1.2)
    # 자산 soft (6차원)
    vec_asset = soft_encode(asset_idx, len(ASSET_BUCKETS), spread=1.2)

    vec  = vec_ind + vec_age + vec_asset
    norm = float(np.linalg.norm(vec))
    return [round(v / norm, 6) for v in vec] if norm > 0 else vec


def get_industry_label(raw: str) -> str:
    return map_industry(raw)


def get_age_label(years: float) -> str:
    idx = age_to_bucket(years)
    return AGE_BUCKETS[idx]


def get_asset_label(asset_bil: float) -> str:
    idx = asset_to_bucket(asset_bil)
    return ASSET_BUCKETS[idx]
