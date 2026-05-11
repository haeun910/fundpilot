import { ELIGIBILITY_COLOR, RISK_COLOR } from "@/lib/constants"
import type { EligibilityStatus, RiskLevel } from "@/lib/types"

export function EligibilityBadge({ status }: { status: EligibilityStatus }) {
  const label = { "가능": "신청 가능", "조건부": "조건부", "제한": "신청 제한" }[status]
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded border ${ELIGIBILITY_COLOR[status]}`}>
      {label}
    </span>
  )
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded border ${RISK_COLOR[level]}`}>
      리스크 {level}
    </span>
  )
}
