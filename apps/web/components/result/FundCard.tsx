"use client"

import { useState } from "react"
import type { FundRecommendation } from "@/lib/types"
import { EligibilityBadge } from "@/components/ui/Badge"

interface Props {
  rec:   FundRecommendation
  isTop: boolean
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-[#1B3A6B] rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-sm font-medium text-[#1B3A6B] w-9 text-right">{pct}%</span>
    </div>
  )
}

function InfoItem({ label, value }: { label: string; value: string | number | null }) {
  if (value == null) return null
  return (
    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-sm font-medium text-gray-800">{value}</p>
    </div>
  )
}

export function FundCard({ rec, isTop }: Props) {
  const [checklistOpen, setChecklistOpen] = useState(false)

  return (
    <div className={`card p-4 ${isTop ? "border-[#1B3A6B]" : ""}`}>
      {/* 상단 */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium w-5 ${isTop ? "text-[#1B3A6B]" : "text-gray-400"}`}>
            {String(rec.rank).padStart(2, "0")}
          </span>
          <div>
            <p className="text-sm font-medium text-gray-900">{rec.display_name}</p>
            <p className="text-xs text-gray-400 mt-0.5">{rec.category}</p>
          </div>
        </div>
        <EligibilityBadge status={rec.eligibility} />
      </div>

      {/* 적합도 바 */}
      <div className="mb-4">
        <ScoreBar score={rec.score} />
      </div>

      {/* 자금 정보 그리드 */}
      <div className="grid grid-cols-3 gap-3 p-3 bg-gray-50 rounded mb-3">
        <InfoItem label="금리"     value={rec.interest_rate    != null ? `${rec.interest_rate}%`                    : null} />
        <InfoItem label="융자한도" value={rec.limit_amount_bil != null ? `${rec.limit_amount_bil.toLocaleString()}억` : null} />
        <InfoItem label="평균 대출" value={rec.avg_loan_mil    != null ? `${rec.avg_loan_mil.toFixed(0)}백만원`       : null} />
        <InfoItem label="승인율"   value={rec.approval_rate   != null ? `${rec.approval_rate}%`                    : null} />
        <InfoItem label="평균 업력" value={rec.avg_age_years   != null ? `${rec.avg_age_years}년`                    : null} />
        <InfoItem label="평균 자산" value={rec.avg_beneficiary_asset_bil != null ? `${rec.avg_beneficiary_asset_bil}억` : null} />
      </div>

      {/* 수혜 패턴 */}
      <div className="flex flex-wrap gap-3 text-xs text-gray-500 mb-3">
        {rec.top_industries.length > 0 && (
          <span>주요 업종: <span className="text-gray-700">{rec.top_industries.join(" · ")}</span></span>
        )}
        {rec.top_regions.length > 0 && (
          <span>주요 지역: <span className="text-gray-700">{rec.top_regions.slice(0, 3).join(" · ")}</span></span>
        )}
      </div>

      {/* 추천 근거 */}
      <div className="space-y-1 mb-3">
        {rec.match_reasons.map((r, i) => (
          <p key={i} className="text-xs text-gray-500 flex gap-1.5">
            <span className="text-[#1B3A6B] mt-0.5 shrink-0">—</span>{r}
          </p>
        ))}
      </div>

      {/* 제한 사유 */}
      {rec.eligibility !== "가능" && rec.eligibility_reasons.length > 0 && (
        <div className="mb-3 pt-2 border-t border-gray-100">
          {rec.eligibility_reasons.map((r, i) => (
            <p key={i} className="text-xs text-amber-600">{r}</p>
          ))}
        </div>
      )}

      {/* 공고·신청 정보 */}
      <div className="pt-3 border-t border-gray-100">
        {/* 접수 기간 / 문의 */}
        <div className="flex flex-wrap gap-x-4 gap-y-1 mb-3">
          {rec.apply_period && (
            <p className="text-xs text-gray-500">
              <span className="font-medium text-gray-600">접수기간</span>{" "}
              {rec.apply_period}
            </p>
          )}
          {rec.contact && (
            <p className="text-xs text-gray-500">
              <span className="font-medium text-gray-600">문의</span>{" "}
              {rec.contact}
            </p>
          )}
        </div>

        {/* 버튼 행 */}
        <div className="flex gap-2 flex-wrap">
          {rec.apply_url && (
            <a
              href={rec.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5
                         bg-[#1B3A6B] text-white rounded hover:bg-[#152d57] transition-colors"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M2 6h8M6 2l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              온라인 신청
            </a>
          )}
          {rec.guide_url && (
            <a
              href={rec.guide_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5
                         border border-gray-200 text-gray-600 rounded hover:border-[#1B3A6B] hover:text-[#1B3A6B] transition-colors"
            >
              공고 안내
            </a>
          )}
          {rec.checklist.length > 0 && (
            <button
              type="button"
              onClick={() => setChecklistOpen(o => !o)}
              className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5
                         border border-gray-200 text-gray-600 rounded hover:border-[#1B3A6B] hover:text-[#1B3A6B] transition-colors"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <rect x="1" y="1" width="10" height="10" rx="2" stroke="currentColor" strokeWidth="1.2"/>
                <path d="M3.5 6l2 2 3-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              신청 체크리스트
              <svg
                width="10" height="10" viewBox="0 0 10 10" fill="none"
                className={`transition-transform ${checklistOpen ? "rotate-180" : ""}`}
              >
                <path d="M2 3.5l3 3 3-3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
              </svg>
            </button>
          )}
        </div>

        {/* 체크리스트 展開 */}
        {checklistOpen && rec.checklist.length > 0 && (
          <div className="mt-3 space-y-3">
            {rec.checklist.map((cat, ci) => (
              <div key={ci}>
                <p className="text-xs font-medium text-gray-700 mb-1.5">{cat.category}</p>
                <ul className="space-y-1">
                  {cat.items.map((item, ii) => (
                    <li key={ii} className="flex gap-2 text-xs text-gray-600">
                      <span className="text-[#1B3A6B] shrink-0 mt-0.5">✓</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
