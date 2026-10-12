"""제주 버스 API: 주변 정류장, 실시간 도착 예정, 경유 노선.

도착·경유 노선은 bus.jeju.go.kr(JSON, 정보가 더 풍부)을 먼저 시도하고, 실패하면 JTBIS(XML)로 전환한다.
bus.jeju.go.kr은 중간 인증서 누락으로 환경에 따라 연결이 실패하므로, 실패 후 일정 시간은 바로 JTBIS를 쓴다.
"""

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Path, Query

import cache
from config import (
    ARRIVALS_TTL,
    BUS_ROUTES_TTL,
    JEJU_BUS_API_BASE,
    JTBIS_API_BASE,
    JTBIS_BUS_URL,
    JTBIS_STATION_URL,
    KST,
    PRIMARY_RETRY_AFTER,
    ROUTES_TTL,
    STATIONS_TTL,
)
from http_client import UpstreamError, fetch_text
from services import jeju_bus

router = APIRouter(prefix="/api/bus", tags=["bus"])

StationId = Path(pattern=r"^\d{6,10}$", description="BIS 정류장 ID (예: 405000153)")

SOURCE_PRIMARY = "bus.jeju.go.kr"
SOURCE_FALLBACK = "jtbis"
_PRIMARY_DOWN_KEY = "primary_down"


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


async def _get_bus_routes() -> dict[str, dict[str, Any]]:
    routes = cache.get("bus_routes")
    if routes is None:
        routes = jeju_bus.parse_bus_routes(await fetch_text(JTBIS_BUS_URL))
        cache.set("bus_routes", routes, BUS_ROUTES_TTL)
    return routes


async def _with_fallback(
    primary: Callable[[], Awaitable[list[dict[str, Any]]]],
    fallback: Callable[[], Awaitable[list[dict[str, Any]]]],
) -> tuple[list[dict[str, Any]], str]:
    """bus.jeju.go.kr → 실패 시 JTBIS. 둘 다 실패하면 502."""
    if cache.get(_PRIMARY_DOWN_KEY) is None:
        try:
            return await primary(), SOURCE_PRIMARY
        except (UpstreamError, ValueError) as e:
            print(f"[bus] {SOURCE_PRIMARY} failed, using {SOURCE_FALLBACK}: {e!r}")
            cache.set(_PRIMARY_DOWN_KEY, True, PRIMARY_RETRY_AFTER)
    try:
        return await fallback(), SOURCE_FALLBACK
    except (UpstreamError, ValueError) as e:
        raise _upstream_failed(e) from e


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

        async def primary():
            url = f"{JEJU_BUS_API_BASE}/searchArrivalInfoList.do?{urlencode({'station_id': station_id})}"
            return jeju_bus.parse_arrivals(await fetch_text(url))

        async def fallback():
            routes = await _get_bus_routes()
            url = f"{JTBIS_API_BASE}/BusArrives?{urlencode({'station': station_id})}"
            return jeju_bus.parse_jtbis_arrivals(await fetch_text(url), routes)

        arrivals, source = await _with_fallback(primary, fallback)
        data = {"stationId": station_id, "arrivals": arrivals, "source": source, "fetchedAt": _now()}
        cache.set(key, data, ARRIVALS_TTL)
    return data


@router.get("/stations/{station_id}/routes")
async def station_routes(station_id: str = StationId):
    key = f"routes:{station_id}"
    data = cache.get(key)
    if data is None:

        async def primary():
            url = f"{JEJU_BUS_API_BASE}/searchRouteByStationList.do?{urlencode({'station_id': station_id})}"
            return jeju_bus.parse_routes(await fetch_text(url))

        async def fallback():
            routes = await _get_bus_routes()
            url = f"{JTBIS_API_BASE}/StationRoutePs?{urlencode({'station': station_id})}"
            return jeju_bus.parse_jtbis_station_routes(await fetch_text(url), routes)

        routes, source = await _with_fallback(primary, fallback)
        data = {"stationId": station_id, "routes": routes, "source": source, "fetchedAt": _now()}
        cache.set(key, data, ROUTES_TTL)
    return data
