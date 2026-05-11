import type { ContributionInfo } from "@/lib/types"

interface Props {
  contributions: ContributionInfo
}

const ITEMS: Array<{ key: keyof ContributionInfo; label: string }> = [
  { key: "업종",    label: "업종" },
  { key: "업력",    label: "업력" },
  { key: "자산규모", label: "자산 규모" },
]

export function ContributionBar({ contributions }: Props) {
  return (
    <div className="space-y-2">
      {ITEMS.map(({ key, label }) => {
        const pct = Math.round((contributions[key] ?? 0) * 100)
        return (
          <div key={key} className="flex items-center gap-3">
            <span className="text-xs text-gray-500 w-16 shrink-0">{label}</span>
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-[#1B3A6B]/70 rounded-full"
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 w-8 text-right">{pct}%</span>
          </div>
        )
      })}
    </div>
  )
}
