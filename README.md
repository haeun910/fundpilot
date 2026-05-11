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
│
├── apps/
│   │
│   ├── web/                          # Next.js 14 (App Router)
│   │   ├── app/
│   │   │   ├── page.tsx              # 기업 정보 입력 (메인)
│   │   │   ├── result/
│   │   │   │   └── page.tsx          # 분석 결과
│   │   │   ├── compare/
│   │   │   │   └── page.tsx          # 정책자금 비교
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   │
│   │   ├── components/
│   │   │   ├── form/
│   │   │   │   ├── CompanyForm.tsx   # 기업 정보 입력 폼
│   │   │   │   ├── IndustrySelect.tsx
│   │   │   │   └── FormField.tsx
│   │   │   │
│   │   │   ├── result/
│   │   │   │   ├── FundCard.tsx      # 추천 정책자금 카드
│   │   │   │   ├── RiskBadge.tsx     # 리스크 등급 배지
│   │   │   │   ├── EligibilityTag.tsx # 신청가능/제한 태그
│   │   │   │   └── FeatureBar.tsx    # 영향 요소 바 차트
│   │   │   │
│   │   │   ├── chart/
│   │   │   │   ├── SuitabilityChart.tsx  # 적합도 차트 (Recharts)
│   │   │   │   ├── RadarChart.tsx        # 기업 비교 레이더
│   │   │   │   └── ContributionBar.tsx   # XAI 기여도 바
│   │   │   │
│   │   │   └── ui/
│   │   │       ├── Button.tsx
│   │   │       ├── Badge.tsx
│   │   │       ├── Card.tsx
│   │   │       └── Tooltip.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts               # FastAPI 호출 함수
│   │   │   ├── types.ts             # 공통 타입 정의
│   │   │   └── constants.ts         # 업종 목록, 지역 등
│   │   │
│   │   ├── package.json
│   │   ├── next.config.ts
│   │   └── tailwind.config.ts
│   │
│   └── api/                         # FastAPI (Python 3.11)
│       ├── main.py                  # 앱 진입점, CORS 설정
│       │
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── analyze.py           # POST /analyze (신청가능여부)
│       │   ├── recommend.py         # POST /recommend (TOP5 추천)
│       │   └── risk.py              # POST /risk (리스크 분석)
│       │   └── funds.py             # GET  /funds   — 자금 정보 조회
│       ├── services/
│       │   ├── __init__.py
│       │   ├── rule_engine.py       # 융자제외업종 + 부채비율 검증
│       │   ├── recommender.py       # Cosine Similarity 추천
│       │   ├── risk_analyzer.py     # Isolation Forest 리스크
│       │   └── explainer.py         # Feature Contribution (XAI)
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── models.py            # Pydantic 요청/응답 스키마
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py            # 환경변수, 데이터 경로 설정
│       │
│       ├── requirements.txt
│       └── Dockerfile
│
├── packages/
│   └── ml/                          # AI/ML 모듈 (api/services에서 import)
│       ├── __init__.py
│       ├── preprocessor.py          # 입력 벡터화 (StandardScaler, One-Hot)
│       ├── cosine_model.py          # Cosine Similarity 추천 엔진
│       ├── kmeans_model.py          # K-Means 기업 유형 분류
│       └── isolation_model.py       # Isolation Forest 리스크 분석
│
├── data/
│   ├── raw/                         # 원본 공공데이터 CSV (23개)
│   │
│   ├── processed/                   # 전처리 결과 JSON (API가 로드)
│   │   ├── fund_patterns.json       # 정책자금별 표준 수혜 패턴 벡터
│   │   ├── fund_info.json           # 자금명 · 한도 · 금리
│   │   ├── exclusion_rules.json     # 융자제외 업종 33개
│   │   └── debt_limits.json         # 업종별 부채비율 제한
│   │
│   └── scripts/
│       ├── preprocess.py            # CSV → JSON 전처리 메인
│       └── generate_patterns.py     # 표준 수혜 패턴 벡터 생성
│
├── package.json                     # workspaces 설정
├── turbo.json                       # Turborepo 빌드 파이프라인
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
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
