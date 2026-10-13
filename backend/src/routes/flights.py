"""공항 API: 주변 공항, 공항 실시간 출발/도착 현황.

- 실시간 현황: 한국공항공사 실시간 항공기 운항정보 검색 GW(flight-search/info)
실시간 현황은 공공데이터포털 인증키(DATA_GO_KR_SERVICE_KEY)가 필요하다. 주변 공항 검색은 키 없이 동작한다.
"""

from datetime import datetime
from typing import Any, Literal
from urllib.parse import unquote, urlencode

from fastapi import APIRouter, HTTPException, Path, Query

import cache
from config import (
    DATA_GO_KR_SERVICE_KEY,
    FLIGHT_STATUS_TTL,
    KAC_FLIGHT_STATUS_URL,
    KST,
)
from http_client import UpstreamError, fetch_text
from services import flights

router = APIRouter(prefix="/api/flights", tags=["flights"])

AirportCode = Path(pattern=r"^[A-Z]{3}$", description="공항 IATA 코드 (예: CJU)")

STATUS_PAGE_SIZE = 100
STATUS_MAX_PAGES = 5


def _now() -> datetime:
    return datetime.now(KST)


def _service_key() -> str:
    if not DATA_GO_KR_SERVICE_KEY:
        raise HTTPException(status_code=503, detail="항공 운항정보 인증키가 설정되지 않았습니다.")
    # 포털의 'Encoding' 키(%2B 등 포함)를 넣어도 urlencode에서 이중 인코딩되지 않도록 원문으로 되돌린다
    return unquote(DATA_GO_KR_SERVICE_KEY) if "%" in DATA_GO_KR_SERVICE_KEY else DATA_GO_KR_SERVICE_KEY


def _airport(code: str) -> dict[str, Any]:
    airport = flights.AIRPORTS_BY_CODE.get(code)
    if airport is None:
        raise HTTPException(status_code=404, detail="지원하지 않는 공항입니다.")
    return airport


def _upstream_failed(e: Exception) -> HTTPException:
    print(f"[flights] upstream error: {e!r}")
    return HTTPException(status_code=502, detail="항공 운항정보 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요.")


@router.get("/airports/nearby")
async def nearby_airports(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius: int = Query(50000, ge=1000, le=300000, description="검색 반경(m)"),
    limit: int = Query(5, ge=1, le=20),
):
    found = flights.find_nearby_airports(lat, lng, radius, limit)
    return {"airports": found, "count": len(found)}


@router.get("/airports/{code}/status")
async def airport_status(
    code: str = AirportCode,
    direction: Literal["departure", "arrival"] = Query("departure"),
):
    """오늘 1시간 전 ~ 6시간 후 출발(또는 도착) 항공편의 실시간 현황(국내·국제선)."""
    airport = _airport(code)
    key = f"flight_status:{code}:{direction}"
    data = cache.get(key)
    if data is None:
        service_key = _service_key()
        now = _now()
        start, end = flights.status_window(now)
        params = {
            "serviceKey": service_key,
            "schAirCode": code,
            "schIOType": "I" if direction == "arrival" else "O",
            "schStTime": start,
            "schEdTime": end,
            "numOfRows": STATUS_PAGE_SIZE,
            "type": "xml",
            # schFln(편명)은 가이드상 필수로 표기되어 있으나 예제 응답은 편명과 무관한 전체 목록이다.
            # 공항 전체 현황이 목적이므로 보내지 않는다(실제 키로 확인 필요, docs/flight-api.md).
        }
        collected: list[dict[str, Any]] = []
        try:
            for page in range(1, STATUS_MAX_PAGES + 1):
                url = f"{KAC_FLIGHT_STATUS_URL}?{urlencode({**params, 'pageNo': page})}"
                items, total = flights.parse_flight_status(await fetch_text(url))
                collected.extend(items)
                if not items or page * STATUS_PAGE_SIZE >= total:
                    break
        except (UpstreamError, ValueError) as e:
            raise _upstream_failed(e) from e
        data = {
            "airport": {"code": code, "name": airport["name"]},
            "direction": direction,
            "flights": [f for f in flights.sort_flights(collected) if f["direction"] == direction],
            "fetchedAt": now.isoformat(timespec="seconds"),
        }
        cache.set(key, data, FLIGHT_STATUS_TTL)
    return data
