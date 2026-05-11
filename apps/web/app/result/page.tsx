"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import type { FullAnalysisResponse, CompanyInput } from "@/lib/types"
import { FundCard } from "@/components/result/FundCard"
import { FundCarousel } from "@/components/result/FundCarousel"
import { ContributionBar } from "@/components/chart/ContributionBar"
import { EligibilityBadge, RiskBadge } from "@/components/ui/Badge"

export default function ResultPage() {
  const router  = useRouter()
  const [result,  setResult]  = useState<FullAnalysisResponse | null>(null)
  const [company, setCompany] = useState<CompanyInput | null>(null)

  useEffect(() => {
    const r = sessionStorage.getItem("fundpilot_result")
    const c = sessionStorage.getItem("fundpilot_company")
    if (!r) { router.replace("/"); return }
    setResult(JSON.parse(r))
    if (c) setCompany(JSON.parse(c))
  }, [router])

  if (!result) return null

  const { company_profile, eligibility, recommendations, risk } = result
  const topRec = recommendations[0]

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">

      {/* 헤더 배너 */}
      <div className="bg-[#1B3A6B] rounded-lg px-6 py-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <p className="text-white/60 text-xs">분석 결과</p>
          <p className="text-white/60 text-xs">
            기준금리 <span className="text-white font-medium">
              {result.base_rate != null ? result.base_rate.toFixed(2) + "%" : "-"}
            </span>
          </p>
        </div>
        <p className="text-white text-base font-medium mb-3">
          {company_profile.industry_category} · 업력 {company_profile.age_label} · 자산 {company_profile.asset_label}
        </p>
        {company_profile.cluster && (
          <div className="flex items-start gap-2 bg-white/10 rounded-lg px-3 py-2">
            <span className="text-white/60 text-xs mt-0.5 shrink-0">기업 유형</span>
            <div>
              <span className="text-white text-sm font-medium">{company_profile.cluster.cluster_label}</span>
              <p className="text-white/70 text-xs mt-0.5">{company_profile.cluster.cluster_desc}</p>
            </div>
          </div>
        )}
      </div>

      {/* 요약 카드 3개 */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="card p-4">
          <p className="text-xs text-gray-400 mb-2">신청 가능 여부</p>
          <EligibilityBadge status={eligibility.overall} />
          {eligibility.debt_limit_info?.limit_ratio && (
            <p className="text-xs text-gray-400 mt-2">
              부채비율 제한 {eligibility.debt_limit_info.limit_ratio}%
            </p>
          )}
        </div>
        <div className="card p-4">
          <p className="text-xs text-gray-400 mb-1">최고 적합도</p>
          <p className="text-2xl font-medium text-[#1B3A6B]">
            {Math.round((topRec?.score ?? 0) * 100)}%
          </p>
          <p className="text-xs text-gray-400 mt-1 truncate">{topRec?.display_name}</p>
        </div>
        <div className="card p-4">
          <p className="text-xs text-gray-400 mb-2">수혜 패턴 리스크</p>
          <RiskBadge level={risk.level} />
          <p className="text-xs text-gray-400 mt-2 truncate">{risk.factors[0]}</p>
        </div>
      </div>

      {/* 신청 제한 사유 (있을 때만) */}
      {eligibility.overall !== "가능" && (
        <div className="card p-4 mb-6 border-amber-200 bg-amber-50">
          <p className="text-xs font-medium text-amber-700 mb-1">신청 주의사항</p>
          {eligibility.reasons.map((r, i) => (
            <p key={i} className="text-xs text-amber-600">{r}</p>
          ))}
        </div>
      )}

      {/* 추천 자금 캐러셀 */}
      <div className="mb-8">
        <p className="section-label mb-4">추천 정책자금 TOP {recommendations.length}</p>
        <FundCarousel recommendations={recommendations} />
      </div>

      {/* 리스크 분석 */}
      <div className="mb-8">
        <p className="section-label mb-4">수혜 패턴 리스크 분석</p>
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-4">
            <RiskBadge level={risk.level} />
            <span className="text-xs text-gray-400">패턴 이탈 점수: {(risk.score * 100).toFixed(0)}점</span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-xs font-medium text-gray-500 mb-2">주요 리스크 요인</p>
              <ul className="space-y-1">
                {risk.factors.map((f, i) => (
                  <li key={i} className="text-xs text-gray-600 flex gap-1.5">
                    <span className="text-red-400 mt-0.5 shrink-0">—</span>{f}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 mb-2">보완 방향</p>
              <ul className="space-y-1">
                {risk.suggestions.map((s, i) => (
                  <li key={i} className="text-xs text-gray-600 flex gap-1.5">
                    <span className="text-[#1B3A6B] mt-0.5 shrink-0">—</span>{s}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* 수혜기업 비교 */}
          {risk.compared_to && Object.keys(risk.compared_to).length > 0 && (
            <div className="pt-4 border-t border-gray-100">
              <p className="text-xs font-medium text-gray-500 mb-3">평균 수혜기업 비교</p>
              <div className="grid grid-cols-3 gap-3">
                {risk.compared_to.avg_age_years != null && (
                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-xs text-gray-400">평균 업력</p>
                    <p className="text-sm font-medium text-gray-700">{risk.compared_to.avg_age_years}년</p>
                    <p className="text-xs text-[#1B3A6B]">내 기업 {risk.compared_to.user_age_years}년</p>
                  </div>
                )}
                {risk.compared_to.avg_asset_bil != null && (
                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-xs text-gray-400">평균 자산</p>
                    <p className="text-sm font-medium text-gray-700">{Number(risk.compared_to.avg_asset_bil).toFixed(0)}억</p>
                    <p className="text-xs text-[#1B3A6B]">내 기업 {risk.compared_to.user_asset_bil}억</p>
                  </div>
                )}
                {risk.compared_to.user_debt_ratio != null && (
                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-xs text-gray-400">내 부채비율</p>
                    <p className="text-sm font-medium text-gray-700">{risk.compared_to.user_debt_ratio}%</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 1위 자금 영향 요소 */}
      {topRec && (
        <div className="mb-8">
          <p className="section-label mb-4">추천 근거 — 영향 요소 분석</p>
          <div className="card p-5">
            <p className="text-xs text-gray-400 mb-4">
              {topRec.display_name} 적합도에 기여한 요소
            </p>
            <ContributionBar contributions={topRec.contributions} />
          </div>
        </div>
      )}

      {/* 다시 분석 */}
      <div className="flex justify-center">
        <button onClick={() => router.push("/")} className="btn-ghost">
          다른 조건으로 다시 분석
        </button>
      </div>
    </div>
  )
}
