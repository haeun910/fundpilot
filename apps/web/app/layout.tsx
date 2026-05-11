import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "FundPilot — 정책자금 추천 플랫폼",
  description: "중소벤처기업진흥공단 공공데이터 기반 AI 정책자금 추천 서비스",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="bg-gray-50 min-h-screen">
        <header className="bg-[#1B3A6B] h-12 flex items-center px-6">
          <span className="text-white text-sm font-medium tracking-tight">FundPilot</span>
          <span className="text-white/50 text-xs ml-3">정책자금 추천 플랫폼</span>
          <span className="ml-auto text-white/40 text-xs">
            중소벤처기업진흥공단 공공데이터 기반 · 2026년 2분기 기준
          </span>
        </header>
        <main>{children}</main>
        <footer className="border-t border-gray-200 mt-16 py-6 text-center text-xs text-gray-400">
          본 서비스는 중소벤처기업진흥공단 공공데이터를 기반으로 하며, 실제 신청 결과와 다를 수 있습니다.
        </footer>
      </body>
    </html>
  )
}
