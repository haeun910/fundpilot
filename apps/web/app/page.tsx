"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { analyze } from "@/lib/api"
import type { CompanyInput, Purpose } from "@/lib/types"
import {
  INDUSTRIES, REGIONS, SPECIAL_TYPES,
  AGE_OPTIONS, ASSET_OPTIONS, DEBT_OPTIONS, EMPLOYEE_OPTIONS,
} from "@/lib/constants"

// 폼 내부 상태 (숫자 대신 선택지 index 저장)
interface FormState {
  industry:        string
  region:          string
  age_idx:         number | null
  asset_idx:       number | null
  debt_idx:        number | null
  employee_idx:    number | null
  purpose:         Purpose
  special_types:   string[]
}

const INIT: FormState = {
  industry:      "",
  region:        "경기",
  age_idx:       null,
  asset_idx:     null,
  debt_idx:      null,
  employee_idx:  null,
  purpose:       "시설+운전",
  special_types: [],
}

const STEPS = ["기업 기본 정보", "재무 현황", "신청 조건"]

// ── 공통 선택 버튼 그룹 ──────────────────────────────────────
function OptionGrid({
  options,
  selected,
  onSelect,
  cols = 2,
}: {
  options: { label: string; value: number | string }[]
  selected: number | null | string
  onSelect: (idx: number) => void
  cols?: number
}) {
  return (
    <div className={`grid gap-2`} style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
      {options.map((opt, i) => {
        const active = typeof selected === "number" ? selected === i : false
        return (
          <button
            key={i}
            type="button"
            onClick={() => onSelect(i)}
            className={`py-2.5 px-3 rounded border text-sm text-left transition-all ${
              active
                ? "bg-[#1B3A6B] text-white border-[#1B3A6B] font-medium"
                : "bg-white text-gray-700 border-gray-200 hover:border-[#1B3A6B] hover:text-[#1B3A6B]"
            }`}
          >
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}

// ── 진행 바 ─────────────────────────────────────────────────
function StepBar({ current, total }: { current: number; total: number }) {
  return (
    <div className="mb-8">
      <div className="flex justify-between mb-2">
        {STEPS.map((label, i) => (
          <span
            key={i}
            className={`text-xs font-medium ${
              i <= current ? "text-[#1B3A6B]" : "text-gray-300"
            }`}
          >
            {label}
          </span>
        ))}
      </div>
      <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-[#1B3A6B] rounded-full transition-all duration-300"
          style={{ width: `${((current + 1) / total) * 100}%` }}
        />
      </div>
    </div>
  )
}

export default function HomePage() {
  const router  = useRouter()
  const [step,    setStep]    = useState(0)
  const [form,    setForm]    = useState<FormState>(INIT)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState<string | null>(null)

  function toggleSpecial(val: string) {
    setForm(prev => ({
      ...prev,
      special_types: prev.special_types.includes(val)
        ? prev.special_types.filter(s => s !== val)
        : [...prev.special_types, val],
    }))
  }

  // 각 단계별 유효성
  const step0Valid = !!form.industry && !!form.region && form.employee_idx !== null
  const step1Valid = form.age_idx !== null && form.asset_idx !== null && form.debt_idx !== null
  const step2Valid = !!form.purpose

  function canNext() {
    if (step === 0) return step0Valid
    if (step === 1) return step1Valid
    return step2Valid
  }

  async function handleSubmit() {
    setError(null)
    setLoading(true)
    try {
      const payload: CompanyInput = {
        industry:       form.industry,
        region:         form.region,
        age_years:      AGE_OPTIONS[form.age_idx!].value as number,
        asset_bil:      ASSET_OPTIONS[form.asset_idx!].value as number,
        debt_ratio:     DEBT_OPTIONS[form.debt_idx!].value as number,
        employee_count: EMPLOYEE_OPTIONS[form.employee_idx!].value as number,
        purpose:        form.purpose,
        special_types:  form.special_types,
      }
      const result = await analyze(payload, 5)
      sessionStorage.setItem("fundpilot_result",  JSON.stringify(result))
      sessionStorage.setItem("fundpilot_company", JSON.stringify(payload))
      router.push("/result")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "분석 중 오류가 발생했습니다")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      {/* 인트로 */}
      <div className="mb-8">
        <p className="text-xs text-[#1B3A6B] font-medium mb-1">중소벤처기업진흥공단 공공데이터 기반</p>
        <h1 className="text-2xl font-medium text-gray-900 mb-2">정책자금 적합도 분석</h1>
        <p className="text-sm text-gray-500">
          기업 정보를 입력하면 신청 가능 여부, 맞춤 정책자금 추천, 리스크를 분석합니다.
        </p>
      </div>

      <StepBar current={step} total={STEPS.length} />

      {/* ── STEP 0: 기업 기본 정보 ── */}
      {step === 0 && (
        <div className="space-y-6">
          <div className="card p-5 space-y-5">
            {/* 업종 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                업종 <span className="text-red-400">*</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                {INDUSTRIES.map(ind => (
                  <button
                    key={ind}
                    type="button"
                    onClick={() => setForm(p => ({ ...p, industry: ind }))}
                    className={`py-2.5 px-3 rounded border text-sm text-left transition-all ${
                      form.industry === ind
                        ? "bg-[#1B3A6B] text-white border-[#1B3A6B] font-medium"
                        : "bg-white text-gray-700 border-gray-200 hover:border-[#1B3A6B] hover:text-[#1B3A6B]"
                    }`}
                  >
                    {ind}
                  </button>
                ))}
              </div>
            </div>

            {/* 지역 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                사업장 소재지 <span className="text-red-400">*</span>
              </label>
              <select
                className="input-base"
                value={form.region}
                onChange={e => setForm(p => ({ ...p, region: e.target.value }))}
              >
                {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>

            {/* 종업원 수 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                종업원 규모 <span className="text-red-400">*</span>
              </label>
              <OptionGrid
                options={EMPLOYEE_OPTIONS}
                selected={form.employee_idx}
                onSelect={i => setForm(p => ({ ...p, employee_idx: i }))}
                cols={3}
              />
            </div>
          </div>
        </div>
      )}

      {/* ── STEP 1: 재무 현황 ── */}
      {step === 1 && (
        <div className="space-y-6">
          <div className="card p-5 space-y-5">
            {/* 업력 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                업력 <span className="text-red-400">*</span>
              </label>
              <p className="text-xs text-gray-400 mb-2">사업자등록일 기준 현재까지 경과 연수</p>
              <OptionGrid
                options={AGE_OPTIONS}
                selected={form.age_idx}
                onSelect={i => setForm(p => ({ ...p, age_idx: i }))}
                cols={2}
              />
            </div>

            {/* 자산 규모 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                총자산 규모 <span className="text-red-400">*</span>
              </label>
              <p className="text-xs text-gray-400 mb-2">최근 결산 기준 재무상태표 상 자산 총계</p>
              <OptionGrid
                options={ASSET_OPTIONS}
                selected={form.asset_idx}
                onSelect={i => setForm(p => ({ ...p, asset_idx: i }))}
                cols={2}
              />
            </div>

            {/* 부채비율 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                부채비율 <span className="text-red-400">*</span>
              </label>
              <p className="text-xs text-gray-400 mb-2">부채 총계 ÷ 자본 총계 × 100</p>
              <OptionGrid
                options={DEBT_OPTIONS}
                selected={form.debt_idx}
                onSelect={i => setForm(p => ({ ...p, debt_idx: i }))}
                cols={2}
              />
              <p className="text-xs text-gray-400 mt-2">
                * 부채비율이 높으면 일부 자금의 신청이 제한될 수 있습니다
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ── STEP 2: 신청 조건 ── */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="card p-5 space-y-5">
            {/* 자금 용도 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                자금 용도 <span className="text-red-400">*</span>
              </label>
              <p className="text-xs text-gray-400 mb-2">신청하려는 자금의 사용 목적을 선택하세요</p>
              <div className="space-y-2">
                {(
                  [
                    { value: "시설+운전", label: "시설 + 운전자금", desc: "설비 구매 및 운영비 모두 해당" },
                    { value: "시설",      label: "시설자금",         desc: "기계·설비·건물 등 자산 취득" },
                    { value: "운전",      label: "운전자금",         desc: "원자재·인건비 등 경영 운영비" },
                  ] as const
                ).map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setForm(p => ({ ...p, purpose: opt.value }))}
                    className={`w-full flex items-start gap-3 p-3 rounded border text-left transition-all ${
                      form.purpose === opt.value
                        ? "bg-[#1B3A6B] text-white border-[#1B3A6B]"
                        : "bg-white border-gray-200 hover:border-[#1B3A6B]"
                    }`}
                  >
                    <div
                      className={`mt-0.5 w-4 h-4 rounded-full border-2 shrink-0 flex items-center justify-center ${
                        form.purpose === opt.value ? "border-white" : "border-gray-300"
                      }`}
                    >
                      {form.purpose === opt.value && (
                        <div className="w-2 h-2 rounded-full bg-white" />
                      )}
                    </div>
                    <div>
                      <p className={`text-sm font-medium ${form.purpose === opt.value ? "text-white" : "text-gray-800"}`}>
                        {opt.label}
                      </p>
                      <p className={`text-xs mt-0.5 ${form.purpose === opt.value ? "text-white/70" : "text-gray-400"}`}>
                        {opt.desc}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* 정책 우대 조건 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                정책 우대 조건
              </label>
              <p className="text-xs text-gray-400 mb-2">해당 인증·지위가 있을 경우 선택하세요 (선택 사항)</p>
              <div className="flex flex-wrap gap-2">
                {SPECIAL_TYPES.map(({ value, label }) => {
                  const active = form.special_types.includes(value)
                  return (
                    <button
                      key={value}
                      type="button"
                      onClick={() => toggleSpecial(value)}
                      className={`text-sm px-3 py-1.5 rounded border transition-colors ${
                        active
                          ? "bg-[#1B3A6B] text-white border-[#1B3A6B]"
                          : "text-gray-600 border-gray-200 hover:border-[#1B3A6B] hover:text-[#1B3A6B]"
                      }`}
                    >
                      {label}
                    </button>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 에러 */}
      {error && (
        <div className="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded px-4 py-3">
          {error}
        </div>
      )}

      {/* 네비게이션 버튼 */}
      <div className={`flex mt-6 gap-3 ${step > 0 ? "justify-between" : "justify-end"}`}>
        {step > 0 && (
          <button
            type="button"
            onClick={() => setStep(s => s - 1)}
            className="btn-ghost px-6"
          >
            이전
          </button>
        )}

        {step < STEPS.length - 1 ? (
          <button
            type="button"
            onClick={() => setStep(s => s + 1)}
            disabled={!canNext()}
            className="btn-primary px-8 disabled:opacity-40"
          >
            다음 단계
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading || !canNext()}
            className="btn-primary px-8 disabled:opacity-40"
          >
            {loading ? "분석 중..." : "적합도 분석 시작"}
          </button>
        )}
      </div>
    </div>
  )
}
