"""제주 버스 API: 주변 정류장, 실시간 도착 예정, 경유 노선."""

from datetime import datetime
from typing import Any
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Path, Query

import cache
from config import (
    ARRIVALS_TTL,
    JEJU_BUS_API_BASE,
    JTBIS_STATION_URL,
    KST,
    ROUTES_TTL,
    STATIONS_TTL,
)
from http_client import UpstreamError, fetch_text
from services import jeju_bus

router = APIRouter(prefix="/api/bus", tags=["bus"])

StationId = Path(pattern=r"^\d{6,10}$", description="BIS 정류장 ID (예: 405000153)")


def _now() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _upstream_failed(e: Exception) -> HTTPException:
    print(f"[bus] upstream error: {e!r}")
    return HTTPException(status_code=502, detail="버스 정보 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요.")


async def _get_stations() -> list[dict[str, Any]]:
    stations = cache.get("stations")
    if stations is None:
        try:
            stations = jeju_bus.parse_stations(await fetch_text(JTBIS_STATION_URL))
        except (UpstreamError, ValueError) as e:
            raise _upstream_failed(e) from e
        cache.set("stations", stations, STATIONS_TTL)
    return stations


@router.get("/stations/nearby")
async def nearby_stations(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    radius: int = Query(1000, ge=100, le=5000, description="검색 반경(m)"),
    limit: int = Query(20, ge=1, le=50),
):
    stations = await _get_stations()
    found = jeju_bus.find_nearby(stations, lat, lng, radius, limit)
    return {"stations": found, "count": len(found)}


@router.get("/stations/{station_id}/arrivals")
async def station_arrivals(station_id: str = StationId):
    key = f"arrivals:{station_id}"
    data = cache.get(key)
    if data is None:
        url = f"{JEJU_BUS_API_BASE}/searchArrivalInfoList.do?{urlencode({'station_id': station_id})}"
        try:
            arrivals = jeju_bus.parse_arrivals(await fetch_text(url))
        except (UpstreamError, ValueError) as e:
            raise _upstream_failed(e) from e
        data = {"stationId": station_id, "arrivals": arrivals, "fetchedAt": _now()}
        cache.set(key, data, ARRIVALS_TTL)
    return data


@router.get("/stations/{station_id}/routes")
async def station_routes(station_id: str = StationId):
    key = f"routes:{station_id}"
    data = cache.get(key)
    if data is None:
        url = f"{JEJU_BUS_API_BASE}/searchRouteByStationList.do?{urlencode({'station_id': station_id})}"
        try:
            routes = jeju_bus.parse_routes(await fetch_text(url))
        except (UpstreamError, ValueError) as e:
            raise _upstream_failed(e) from e
        data = {"stationId": station_id, "routes": routes, "fetchedAt": _now()}
        cache.set(key, data, ROUTES_TTL)
    return data
