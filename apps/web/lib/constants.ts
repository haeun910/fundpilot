export const INDUSTRIES = [
  "금속 제조", "기계·장비 제조", "전기·전력", "전자·반도체",
  "섬유·의류", "화학·화공", "생활용품·잡화", "식품·음료",
  "IT·소프트웨어", "유통·물류", "건설", "서비스·기타",
]

export const REGIONS = [
  "서울", "경기", "인천", "부산", "대구", "광주", "대전",
  "울산", "세종", "강원", "충북", "충남", "전북", "전남",
  "경북", "경남", "제주",
]

export const SPECIAL_TYPES = [
  { value: "사회적기업",    label: "사회적기업" },
  { value: "소셜벤처",      label: "소셜벤처" },
  { value: "예비사회적기업", label: "예비사회적기업" },
  { value: "협동조합",      label: "협동조합" },
  { value: "마을기업",      label: "마을기업" },
  { value: "자활기업",      label: "자활기업" },
  { value: "ESG",          label: "ESG 인증" },
  { value: "수출",          label: "수출기업" },
]

// 업력 선택지 → API에 전달할 숫자 midpoint
export const AGE_OPTIONS = [
  { label: "1년 미만",   value: 0.5  },
  { label: "1 ~ 3년",   value: 2    },
  { label: "3 ~ 5년",   value: 4    },
  { label: "5 ~ 7년",   value: 6    },
  { label: "7 ~ 10년",  value: 8.5  },
  { label: "10 ~ 15년", value: 12.5 },
  { label: "15 ~ 20년", value: 17.5 },
  { label: "20년 이상", value: 25   },
]

// 자산 규모 선택지 (억원)
export const ASSET_OPTIONS = [
  { label: "10억 미만",    value: 5   },
  { label: "10 ~ 30억",   value: 20  },
  { label: "30 ~ 70억",   value: 60  },
  { label: "70 ~ 100억",  value: 85  },
  { label: "100 ~ 200억", value: 150 },
  { label: "200억 이상",  value: 250 },
]

// 부채비율 선택지 (%)
export const DEBT_OPTIONS = [
  { label: "100% 미만",    value: 50  },
  { label: "100 ~ 200%",  value: 150 },
  { label: "200 ~ 300%",  value: 250 },
  { label: "300 ~ 400%",  value: 350 },
  { label: "400% 초과",   value: 450 },
]

// 종업원 수 선택지 (명)
export const EMPLOYEE_OPTIONS = [
  { label: "5인 미만",   value: 3  },
  { label: "5 ~ 10인",  value: 7  },
  { label: "10 ~ 20인", value: 15 },
  { label: "20 ~ 50인", value: 35 },
  { label: "50인 이상", value: 75 },
]

export const ELIGIBILITY_LABEL: Record<string, string> = {
  "가능":  "신청 가능",
  "조건부": "조건부 가능",
  "제한":  "신청 제한",
}

export const RISK_COLOR: Record<string, string> = {
  "낮음": "text-green-700  bg-green-50  border-green-200",
  "보통": "text-amber-700  bg-amber-50  border-amber-200",
  "높음": "text-red-700    bg-red-50    border-red-200",
}

export const ELIGIBILITY_COLOR: Record<string, string> = {
  "가능":  "text-green-700 bg-green-50  border-green-200",
  "조건부": "text-amber-700 bg-amber-50  border-amber-200",
  "제한":  "text-red-700   bg-red-50    border-red-200",
}
