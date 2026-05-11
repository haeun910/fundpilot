"""
preprocess.py 실행 후 fund_info.json 에 공고 메타데이터를 추가하는 패치 스크립트.
실행: python data/scripts/patch_fund_metadata.py
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
FUND_INFO_PATH = ROOT / "data" / "processed" / "fund_info.json"

FUND_META = {
    "창업기반지원": {
        "apply_url": "https://ols.kosmes.or.kr/sbl/SH/SHI/SHSI001M0.do",
        "guide_url": "https://www.kosmes.or.kr/sbl/SH/PMO/SHPMO001M0.do?fundId=STARTUP",
        "apply_period": "연중 수시 접수",
        "contact": "중소벤처기업진흥공단 지역본부 · ☎ 1357",
        "checklist": [
            {"category": "신청 자격", "items": ["창업 후 7년 미만 중소기업","융자 제외 업종 비해당","부채비율 업종별 기준 이하","국세·지방세 체납 없음","대표자 신용불량 없음"]},
            {"category": "준비 서류", "items": ["사업자등록증 사본","최근 2개년 결산 재무제표","부가가치세 과세표준증명원","사업계획서","시설자금: 견적서 또는 계약서","운전자금: 거래처 계약서·발주서","법인등기부등본 (법인)","대표자 신분증 (개인)"]},
            {"category": "신청 절차", "items": ["온라인 사전상담 → 서류 제출 → 현장실사 → 대출 승인 → 자금 집행","처리 기간: 접수 후 약 2~4주"]},
        ],
    },
    "혁신성장지원": {
        "apply_url": "https://ols.kosmes.or.kr/sbl/SH/SHI/SHSI001M0.do",
        "guide_url": "https://www.kosmes.or.kr/sbl/SH/PMO/SHPMO001M0.do?fundId=INNO",
        "apply_period": "연중 수시 접수 (예산 소진 시 마감)",
        "contact": "중소벤처기업진흥공단 지역본부 · ☎ 1357",
        "checklist": [
            {"category": "신청 자격", "items": ["제조·서비스업 중소기업","부채비율 업종별 기준 이하","국세·지방세 체납 없음","융자 제외 업종 비해당"]},
            {"category": "준비 서류", "items": ["사업자등록증 사본","최근 2개년 결산 재무제표","부가가치세 과세표준증명원","사업계획서 (혁신·성장 계획 포함)","기술인증서·특허 (보유 시)","시설자금: 견적서·계약서·배치도","운전자금: 납품계약서·발주서","법인등기부등본 (법인)"]},
            {"category": "우대 조건", "items": ["벤처기업·이노비즈·메인비즈 인증기업 — 금리 우대","스마트공장 도입 기업 — 한도 우대","수출 실적 보유 기업 — 한도 우대","고용창출 기업 — 우선 배정"]},
            {"category": "신청 절차", "items": ["사전상담 예약 → 서류 제출 → 현장실사 → 승인","처리 기간: 접수 후 약 2~4주"]},
        ],
    },
    "제조현장스마트화": {
        "apply_url": "https://ols.kosmes.or.kr/sbl/SH/SHI/SHSI001M0.do",
        "guide_url": "https://www.kosmes.or.kr/sbl/SH/PMO/SHPMO001M0.do",
        "apply_period": "연중 수시 (상반기 조기 마감 가능)",
        "contact": "중소벤처기업진흥공단 · ☎ 1357",
        "checklist": [
            {"category": "신청 자격", "items": ["제조업 영위 중소기업","스마트공장 도입·고도화 계획 보유","융자 제외 업종 비해당","부채비율 제조업 기준 이하"]},
            {"category": "지원 내용", "items": ["시설자금 한정 (운전자금 미지원)","스마트 제조 설비·MES·ERP·SCM 구축","공장 자동화·로봇 도입","에너지 절감 설비 투자"]},
            {"category": "준비 서류", "items": ["사업자등록증 사본","최근 2개년 결산 재무제표","스마트공장 도입 계획서","설비 견적서 및 공급업체 계약서","공장 배치도·설비 배치 계획도","스마트공장 사업 연계 확인서 (해당 시)"]},
            {"category": "신청 절차", "items": ["스마트공장 보급·확산 사업 신청과 병행 추진 권장","사전상담 → 서류 접수 → 현장실사(스마트화 계획 검증) → 승인"]},
        ],
    },
    "netzero": {
        "apply_url": "https://ols.kosmes.or.kr/sbl/SH/SHI/SHSI001M0.do",
        "guide_url": "https://www.kosmes.or.kr/sbl/SH/PMO/SHPMO001M0.do",
        "apply_period": "연중 수시 (탄소중립 이행 계획 보유 기업 우선)",
        "contact": "중소벤처기업진흥공단 · ☎ 1357",
        "checklist": [
            {"category": "신청 자격", "items": ["탄소중립 이행 계획 또는 온실가스 감축 목표 보유","ESG 경영 도입 또는 추진 기업","RE100·CDP 참여 기업 우대","Net-Zero 유망기업 선정 기업 우선 배정"]},
            {"category": "지원 내용", "items": ["탄소저감 설비 (태양광·연료전지·에너지저장장치 등)","친환경 공정 전환 설비 투자","온실가스 감축 기술 개발·도입","운전자금: 친환경 원자재 구매, 녹색 공급망 구축"]},
            {"category": "준비 서류", "items": ["사업자등록증 사본","최근 2개년 결산 재무제표","탄소중립 이행 계획서 또는 감축 목표서","ESG 경영 현황 자료","친환경 설비 견적서 (시설자금)","RE100·CDP 참여 확인서 (해당 시)"]},
            {"category": "신청 절차", "items": ["Net-Zero 유망기업 신청과 자금 연계 추진","사전상담 → 서류 제출 → 탄소중립 계획 검토 → 승인"]},
        ],
    },
    "수출기업글로벌화": {
        "apply_url": "https://ols.kosmes.or.kr/sbl/SH/SHI/SHSI001M0.do",
        "guide_url": "https://www.kosmes.or.kr/sbl/SH/PMO/SHPMO001M0.do",
        "apply_period": "연중 수시 (수출 실적 보유 기업 대상)",
        "contact": "중소벤처기업진흥공단 수출지원부 · ☎ 1357",
        "checklist": [
            {"category": "신청 자격", "items": ["수출 실적 보유 중소기업 (직전연도 또는 최근 2년 내)","해외시장 진출 계획 보유","글로벌 강소기업·수출유망기업 우대","운전자금 전용"]},
            {"category": "지원 내용", "items": ["수출 원자재·부품 구매 비용","해외 마케팅·전시회 참가 비용","수출 인증·표준 취득 비용","해외 현지 법인 설립·운영 초기 비용"]},
            {"category": "준비 서류", "items": ["사업자등록증 사본","수출 실적 증명서 (한국무역협회 발급 또는 수출신고필증)","최근 2개년 결산 재무제표","해외 수출 계약서 또는 구매오더(P.O)","글로벌 진출 계획서","수출유망기업 지정서 (해당 시)"]},
            {"category": "신청 절차", "items": ["수출 실적 증빙 후 온라인 사전상담 예약","서류 제출 → 수출기업 적격 심사 → 승인 → 집행","KOTRA·한국무역협회 연계 프로그램 활용 권장"]},
        ],
    },
    "일시적경영애로": {
        "apply_url": "https://ols.kosmes.or.kr/sbl/SH/SHI/SHSI001M0.do",
        "guide_url": "https://www.kosmes.or.kr/sbl/SH/PMO/SHPMO001M0.do",
        "apply_period": "연중 수시 (긴급 지원 성격으로 신속 처리)",
        "contact": "중소벤처기업진흥공단 지역본부 · ☎ 1357",
        "checklist": [
            {"category": "신청 자격", "items": ["일시적 경영 애로 겪고 있는 중소기업","매출 감소·거래처 부도·원자재 가격 급등 등 외부 요인 피해","자연재해·사고·감염병 등 불가항력적 사유 기업 우대","운전자금 전용"]},
            {"category": "준비 서류", "items": ["사업자등록증 사본","최근 결산 재무제표 및 최근 3개월 부가세 신고자료","경영 애로 입증 서류 (매출 감소 증빙·거래처 도산 확인서 등)","자금 용도 계획서","금융기관 대출 현황 확인서"]},
            {"category": "처리 우대", "items": ["일반 자금 대비 심사 기간 단축 (약 1~2주)","재해·감염병 피해 기업: 서류 간소화 적용 가능","긴급 경영안정자금으로 우선 배정 처리"]},
            {"category": "신청 절차", "items": ["경영 애로 발생 즉시 가까운 중진공 지역본부 방문 또는 온라인 신청","상담 → 긴급 서류 접수 → 신속 심사 → 지원 결정"]},
        ],
    },
}
for key in ["사회적기업","소셜벤처","예비사회적기업","협동조합","마을기업","자활기업"]:
    FUND_META[key] = {
        "apply_url": "https://ols.kosmes.or.kr/sbl/SH/SHI/SHSI001M0.do",
        "guide_url": "https://www.kosmes.or.kr/sbl/SH/PMO/SHPMO001M0.do",
        "apply_period": "연중 수시",
        "contact": "중소벤처기업진흥공단 사회적경제팀 · ☎ 1357",
        "checklist": [],
    }

with open(FUND_INFO_PATH) as f:
    fund_info = json.load(f)

for fund in fund_info["funds"]:
    extra = FUND_META.get(fund["id"], {})
    for k in ("apply_url","guide_url","apply_period","contact","checklist"):
        fund.setdefault(k, extra.get(k, "" if k != "checklist" else []))

with open(FUND_INFO_PATH, "w") as f:
    json.dump(fund_info, f, ensure_ascii=False, indent=2)

print("✅ fund_info.json 메타데이터 패치 완료")
