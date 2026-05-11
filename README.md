# FundPilot

중소벤처기업진흥공단 공공데이터 기반 AI 정책자금 추천 플랫폼

기업 특성과 정책자금별 표준 수혜 패턴을 분석하여 신청 가능한 정책자금과
적합도가 높은 지원사업을 추천하고, 수혜 패턴 이탈 기반 리스크를 제공합니다.

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | Next.js 14 · TypeScript · Tailwind CSS |
| 백엔드 | FastAPI · Python 3.11 |
| AI/ML | scikit-learn (Cosine Similarity · Isolation Forest) |
| 데이터 | 중소벤처기업진흥공단 공공데이터 CSV 23개 |
| 배포 | Vercel (web) · Render (api) |

---

## 프로젝트 구조

```
fundpilot/
├── apps/
│   ├── web/          # Next.js 프론트엔드
│   └── api/          # FastAPI 백엔드
├── packages/
│   └── ml/           # AI/ML 모듈
└── data/
    ├── raw/          # 원본 공공데이터 CSV
    ├── processed/    # 전처리 결과 JSON
    └── scripts/      # 전처리 스크립트
```

---

## 로컬 실행

### 사전 조건

- Python 3.11 이상
- Node.js 20 이상

### 1. 데이터 전처리 (최초 1회)

```bash
pip install pandas numpy scikit-learn
python data/scripts/preprocess.py
```

`data/processed/` 에 JSON 4개가 생성됩니다.

```
exclusion_rules.json   융자제외 업종 33개
debt_limits.json       업종별 부채비율 제한 41개
fund_info.json         정책자금 12개 기본 정보
fund_patterns.json     정책자금별 수혜 패턴 벡터
```

### 2. API 서버

```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

### 3. 웹 서버

```bash
cd apps/web
npm install
npm run dev
```

서비스: http://localhost:3000

---

## Docker로 실행

```bash
# 전처리 먼저 실행 (data/processed/ 생성)
python data/scripts/preprocess.py

# 전체 서비스 기동
docker-compose up --build
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/analyze` | 전체 분석 (추천 + 리스크) |
| GET | `/funds` | 정책자금 목록 |
| GET | `/funds/{id}` | 정책자금 상세 |
| GET | `/funds/{id}/pattern` | 수혜 패턴 데이터 |
| GET | `/health` | 서버 상태 |

### 요청 예시

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company": {
      "industry": "기계 부품 제조",
      "age_years": 7,
      "asset_bil": 50,
      "debt_ratio": 150,
      "employee_count": 25,
      "purpose": "시설+운전",
      "region": "경기",
      "special_types": []
    },
    "top_n": 5
  }'
```

---

## AI 모델 설계

### Rule Engine
융자제외 업종 여부 및 업종별 부채비율 제한을 검증하여
자금별 신청 가능 여부를 판별합니다.

### Cosine Similarity 추천
기업 특성을 25차원 벡터로 변환 후
정책자금별 표준 수혜 패턴 벡터와의 유사도를 계산합니다.

- 업종 (11차원) · 업력 (8차원) · 자산규모 (6차원)
- 집계 통계 기반 수혜 패턴으로 L2 정규화 후 비교

### Isolation Forest 리스크 분석
실제 수혜기업 데이터(약 9,000건)를 학습 데이터로 활용하여
입력 기업이 수혜 패턴에서 얼마나 이탈하는지 분석합니다.

### XAI (Feature Contribution)
추천 점수에 대한 업종·업력·자산규모 각 요소의
기여도를 비율로 제공합니다.

---

## 데이터 출처

중소벤처기업진흥공단 정책자금 공공데이터 (data.go.kr)
2026년 2분기 기준금리 3.14% 적용

---

## 배포

### Vercel (프론트엔드)

```bash
cd apps/web
npx vercel --prod
```

### Render (백엔드)

`apps/api/` 를 Render Web Service로 배포합니다.

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment: `DATA_DIR=data/processed`
