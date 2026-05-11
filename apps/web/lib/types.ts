export type EligibilityStatus = "가능" | "조건부" | "제한"
export type RiskLevel         = "낮음" | "보통" | "높음"
export type Purpose           = "시설" | "운전" | "시설+운전"

export interface CompanyInput {
  industry:       string
  age_years:      number
  asset_bil:      number
  debt_ratio:     number
  employee_count: number
  purpose:        Purpose
  region:         string
  special_types:  string[]
}

export interface ClusterInfo {
  cluster_id:    number
  cluster_label: string
  cluster_desc:  string
  distance:      number
}

export interface CompanyProfile {
  industry_category: string
  age_label:         string
  asset_label:       string
  cluster:           ClusterInfo | null
}

export interface EligibilityResult {
  status:  EligibilityStatus
  reasons: string[]
}

export interface DebtLimitInfo {
  industry:    string | null
  avg_ratio:   number | null
  limit_ratio: number | null
}

export interface FundEligibility {
  overall:         EligibilityStatus
  reasons:         string[]
  by_fund:         Record<string, EligibilityResult>
  debt_limit_info: DebtLimitInfo | null
}

export interface ContributionInfo {
  업종:    number
  업력:    number
  자산규모: number
}

export interface ChecklistCategory {
  category: string
  items:    string[]
}

export interface FundRecommendation {
  fund_id:      string
  display_name: string
  category:     string
  special_type: string | null
  rank:         number

  score:       number
  similarity:  number
  eligibility: EligibilityStatus
  eligibility_reasons: string[]

  interest_rate:             number | null
  limit_amount_bil:          number | null
  avg_loan_mil:              number | null
  approval_rate:             number | null
  avg_beneficiary_asset_bil: number | null

  top_industries: string[]
  top_regions:    string[]
  avg_age_years:  number | null
  purpose_ratio:  Record<string, number>

  contributions: ContributionInfo
  match_reasons: string[]

  apply_url:    string | null
  guide_url:    string | null
  apply_period: string | null
  contact:      string | null
  checklist:    ChecklistCategory[]
}

export interface RiskResult {
  level:       RiskLevel
  score:       number
  factors:     string[]
  suggestions: string[]
  compared_to: Record<string, number | null>
}

export interface FullAnalysisResponse {
  company_profile: CompanyProfile
  eligibility:     FundEligibility
  recommendations: FundRecommendation[]
  risk:            RiskResult
  total:           number
  base_rate:       number | null
}
