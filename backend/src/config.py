"""NearMe Backend 설정."""

import os
from datetime import timedelta, timezone

KST = timezone(timedelta(hours=9))

# 제주 BIS(JTBIS) OpenAPI: 키 불필요, http 전용, XML
JTBIS_API_BASE = "http://busopen.jeju.go.kr/OpenAPI/service/bis"
JTBIS_STATION_URL = f"{JTBIS_API_BASE}/Station"  # 전체 정류장 1회 응답(약 1.1MB)
JTBIS_BUS_URL = f"{JTBIS_API_BASE}/Bus"  # 전체 노선 목록(routeId → 노선번호/행선지)

# 제주 버스정보 JSON API: 키 불필요, https (http 요청 시 302로 https 이동)
# 이 서버는 중간 인증서를 보내지 않아 환경에 따라 TLS 검증이 실패한다(2026-10-12 확인).
# 실패하면 JTBIS로 자동 전환한다.
JEJU_BUS_API_BASE = "https://bus.jeju.go.kr/api"
PRIMARY_RETRY_AFTER = 10 * 60  # bus.jeju.go.kr 실패 후 다시 시도하기까지(초)

# 캐시 유지 시간(초)
STATIONS_TTL = 24 * 60 * 60  # 정류장 목록은 자주 바뀌지 않음
ARRIVALS_TTL = 20  # 실시간 도착 정보
ROUTES_TTL = 60 * 60  # 정류장 경유 노선
BUS_ROUTES_TTL = 24 * 60 * 60  # JTBIS 전체 노선 목록

# 공공데이터포털(data.go.kr) 인증키: 한국공항공사 운항정보·TAGO 국내항공운항정보 공용.
# 저장소에 넣지 않고 환경변수로 주입한다(로컬: backend/.env 대신 셸 환경변수, Cloud Run: --update-env-vars).
# 포털의 'Encoding'/'Decoding' 키 어느 쪽을 넣어도 동작한다.
DATA_GO_KR_SERVICE_KEY = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()

# 한국공항공사 항공기 운항정보 OpenAPI v2.1: 실시간 출발/도착 현황(XML 전용, http 전용)
KAC_FLIGHT_STATUS_URL = "http://openapi.airport.co.kr/service/rest/FlightStatusList/getFlightStatusList"
# 국토교통부 TAGO 국내항공운항정보 v1.0: 출/도착 공항·날짜별 운항 스케줄과 운임(JSON)
TAGO_FLIGHT_URL = "https://apis.data.go.kr/1613000/DmstcFlightNvgInfoService/getFlightOpratInfoList"

FLIGHT_STATUS_TTL = 60  # 공항 실시간 운항 현황
FLIGHT_SCHEDULE_TTL = 30 * 60  # 노선별 운항 스케줄·운임(제공기관 갱신주기 1시간)

UPSTREAM_TIMEOUT = 8.0  # 외부 API 응답 대기(초)

# 브라우저에서 Backend를 직접 호출할 수 있는 Frontend 주소
# (로컬 개발은 Vite 프록시를 쓰므로 같은 출처로 취급되어 필요 없음)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://nearme.greenfeild0514.workers.dev",
]
