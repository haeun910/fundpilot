"use client"

import { useState, useRef } from "react"
import type { FundRecommendation } from "@/lib/types"
import { FundCard } from "./FundCard"

interface Props {
  recommendations: FundRecommendation[]
}

export function FundCarousel({ recommendations }: Props) {
  const [current, setCurrent] = useState(0)
  const touchStartX = useRef<number | null>(null)
  const total = recommendations.length

  function prev() { setCurrent(i => (i - 1 + total) % total) }
  function next() { setCurrent(i => (i + 1) % total) }

  function onTouchStart(e: React.TouchEvent) {
    touchStartX.current = e.touches[0].clientX
  }
  function onTouchEnd(e: React.TouchEvent) {
    if (touchStartX.current === null) return
    const dx = e.changedTouches[0].clientX - touchStartX.current
    if (dx < -40) next()
    else if (dx > 40) prev()
    touchStartX.current = null
  }

  return (
    <div className="relative select-none">
      {/* 슬라이드 영역 */}
      <div
        className="overflow-hidden"
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
      >
        <div
          className="flex transition-transform duration-300 ease-in-out"
          style={{ transform: `translateX(-${current * 100}%)` }}
        >
          {recommendations.map(rec => (
            <div key={rec.fund_id} className="w-full shrink-0">
              <FundCard rec={rec} isTop={rec.rank === 1} />
            </div>
          ))}
        </div>
      </div>

      {/* 하단 컨트롤 */}
      <div className="flex items-center justify-between mt-4 px-1">
        {/* 이전 버튼 */}
        <button
          onClick={prev}
          disabled={total <= 1}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-[#1B3A6B] disabled:opacity-30 transition-colors"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8l4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          이전
        </button>

        {/* 도트 + 카운터 */}
        <div className="flex flex-col items-center gap-2">
          <div className="flex gap-1.5">
            {recommendations.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrent(i)}
                className={`rounded-full transition-all duration-200 ${
                  i === current
                    ? "w-5 h-1.5 bg-[#1B3A6B]"
                    : "w-1.5 h-1.5 bg-gray-200 hover:bg-gray-300"
                }`}
              />
            ))}
          </div>
          <span className="text-xs text-gray-400">
            {current + 1} / {total}
          </span>
        </div>

        {/* 다음 버튼 */}
        <button
          onClick={next}
          disabled={total <= 1}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-[#1B3A6B] disabled:opacity-30 transition-colors"
        >
          다음
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  )
}
