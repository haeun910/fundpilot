import type { CompanyInput, FullAnalysisResponse } from "./types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function analyze(
  company: CompanyInput,
  top_n = 5,
): Promise<FullAnalysisResponse> {
  const res = await fetch(`${BASE}/analyze`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ company, top_n }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `API 오류 (${res.status})`)
  }
  return res.json()
}

export async function getFunds() {
  const res = await fetch(`${BASE}/funds`)
  if (!res.ok) throw new Error("자금 목록 조회 실패")
  return res.json()
}
