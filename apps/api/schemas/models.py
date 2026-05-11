from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, field_validator


# ── 요청 ────────────────────────────────────────────────────

class CompanyInput(BaseModel):
    industry:       str   = Field(..., description="업종 (자유 텍스트)")
    age_years:      float = Field(..., ge=0, le=100,  description="업력 (년)")
    asset_bil:      float = Field(..., ge=0,           description="자산 규모 (억원)")
    debt_ratio:     float = Field(..., ge=0, le=5000,  description="부채비율 (%)")
    employee_count: int   = Field(default=10, ge=1,    description="종업원 수")
    purpose: Literal["시설", "운전", "시설+운전"] = Field(default="시설+운전")
    region:         str   = Field(default="기타")
    special_types:  list[str] = Field(default_factory=list)

    @field_validator("industry")
    @classmethod
    def industry_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("업종을 입력해주세요")
        return v.strip()


class RecommendRequest(BaseModel):
    company: CompanyInput
    top_n:   int = Field(default=5, ge=1, le=12)


class RiskRequest(BaseModel):
    company: CompanyInput
    fund_id: str | None = None


# ── 공통 서브모델 ────────────────────────────────────────────

class EligibilityResult(BaseModel):
    status:  Literal["가능", "조건부", "제한"]
    reasons: list[str]


class DebtLimitInfo(BaseModel):
    industry:    str | None
    avg_ratio:   float | None
    limit_ratio: float | None


class FundEligibility(BaseModel):
    overall:         Literal["가능", "조건부", "제한"]
    reasons:         list[str]
    by_fund:         dict[str, EligibilityResult]
    debt_limit_info: DebtLimitInfo | None


class ContributionInfo(BaseModel):
    업종:    float = 0.0
    업력:    float = 0.0
    자산규모: float = 0.0


class ChecklistCategory(BaseModel):
    category: str
    items:    list[str]


class FundRecommendation(BaseModel):
    fund_id:      str
    display_name: str
    category:     str
    special_type: str | None
    rank:         int

    score:       float
    similarity:  float
    eligibility: Literal["가능", "조건부", "제한"]
    eligibility_reasons: list[str]

    interest_rate:             float | None
    limit_amount_bil:          float | None
    avg_loan_mil:              float | None
    approval_rate:             float | None
    avg_beneficiary_asset_bil: float | None

    top_industries: list[str]
    top_regions:    list[str]
    avg_age_years:  float | None
    purpose_ratio:  dict[str, float]

    contributions: ContributionInfo
    match_reasons: list[str]

    # 공고·체크리스트
    apply_url:    str | None = None
    guide_url:    str | None = None
    apply_period: str | None = None
    contact:      str | None = None
    checklist:    list[ChecklistCategory] = []


class ClusterInfo(BaseModel):
    cluster_id:    int
    cluster_label: str
    cluster_desc:  str
    distance:      float   # 0=전형적, 1=경계


class CompanyProfile(BaseModel):
    industry_category: str
    age_label:         str
    asset_label:       str
    cluster:           ClusterInfo | None = None


class RiskResult(BaseModel):
    level:       Literal["낮음", "보통", "높음"]
    score:       float
    factors:     list[str]
    suggestions: list[str]
    compared_to: dict


# ── 응답 ────────────────────────────────────────────────────

class FullAnalysisResponse(BaseModel):
    company_profile: CompanyProfile
    eligibility:     FundEligibility
    recommendations: list[FundRecommendation]
    risk:            RiskResult
    total:           int
    base_rate:       float | None = None
