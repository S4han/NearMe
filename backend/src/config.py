"""NearMe Backend 설정."""

from datetime import timedelta, timezone

KST = timezone(timedelta(hours=9))

# 제주 BIS(JTBIS) 정류장 목록: 키 불필요, http 전용, XML, 전체 목록 1회 응답(약 1.1MB)
JTBIS_STATION_URL = "http://busopen.jeju.go.kr/OpenAPI/service/bis/Station"

# 제주 버스정보 JSON API: 키 불필요, https (http 요청 시 302로 https 이동)
JEJU_BUS_API_BASE = "https://bus.jeju.go.kr/api"

# 캐시 유지 시간(초)
STATIONS_TTL = 24 * 60 * 60  # 정류장 목록은 자주 바뀌지 않음
ARRIVALS_TTL = 20  # 실시간 도착 정보
ROUTES_TTL = 60 * 60  # 정류장 경유 노선

UPSTREAM_TIMEOUT = 8.0  # 외부 API 응답 대기(초)

# 브라우저에서 Backend를 직접 호출할 수 있는 Frontend 주소
# (로컬 개발은 Vite 프록시를 쓰므로 같은 출처로 취급되어 필요 없음)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://nearme.greenfeild0514.workers.dev",
]
