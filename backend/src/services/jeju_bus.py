"""제주 버스 API 응답을 NearMe 표준 JSON 형태로 변환.

외부 호출 없이 문자열만 다루므로 단위 테스트가 쉽다. 필드 정의는 docs/jeju-bus-api.md 참고.
"""

import json
import math
import xml.etree.ElementTree as ET
from typing import Any

DIRECTIONS = {"N", "S", "E", "W"}


def _text(item: ET.Element, tag: str) -> str:
    return (item.findtext(tag) or "").strip()


def parse_stations(xml_text: str) -> list[dict[str, Any]]:
    """JTBIS Station XML → 사용 중(useYn=Y)인 정류장 목록."""
    root = ET.fromstring(xml_text)
    result_code = root.findtext("./header/resultCode")
    if result_code not in (None, "00"):
        raise ValueError(f"JTBIS resultCode={result_code}")

    stations = []
    for item in root.iter("item"):
        if _text(item, "useYn") != "Y":
            continue
        try:
            lng = float(_text(item, "localX"))
            lat = float(_text(item, "localY"))
        except ValueError:
            continue
        station_id = _text(item, "stationId")
        if not station_id or not (-90 <= lat <= 90 and -180 <= lng <= 180):
            continue
        direction = _text(item, "dirTp").upper()
        stations.append(
            {
                "id": station_id,
                "name": _text(item, "stationNm"),
                "lat": lat,
                "lng": lng,
                "direction": direction if direction in DIRECTIONS else None,
            }
        )
    return stations


def distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """두 좌표 사이 직선거리(m), 하버사인 공식."""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lng2 - lng1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def find_nearby(
    stations: list[dict[str, Any]], lat: float, lng: float, radius: float, limit: int
) -> list[dict[str, Any]]:
    """반경 안의 정류장을 가까운 순으로 최대 limit개."""
    found = []
    for s in stations:
        d = distance_m(lat, lng, s["lat"], s["lng"])
        if d <= radius:
            found.append({**s, "distance": round(d)})
    found.sort(key=lambda s: s["distance"])
    return found[:limit]


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _load_list(json_text: str) -> list[dict[str, Any]]:
    data = json.loads(json_text) if json_text.strip() else []
    if not isinstance(data, list):
        raise ValueError("expected a JSON array")
    return [d for d in data if isinstance(d, dict)]


def parse_arrivals(json_text: str) -> list[dict[str, Any]]:
    """bus.jeju.go.kr searchArrivalInfoList → 도착 예정 목록(빠른 순)."""
    arrivals = []
    for d in _load_list(json_text):
        minutes = _int(d.get("PREDICT_TRAV_TM"))
        if minutes is None:
            continue
        arrivals.append(
            {
                "routeId": str(d.get("ROUTE_ID", "")),
                "routeNum": str(d.get("ROUTE_NUM", "")),
                "destination": str(d.get("ROUTE_SUB_NM", "")),
                "minutes": minutes,
                "remainStations": _int(d.get("REMAIN_STATION")),
                "currentStationName": str(d.get("CURR_STATION_NM", "")),
                "plateNo": str(d.get("PLATE_NO", "")),
                "lowFloor": d.get("LOW_PLATE_TP") == "Y",
            }
        )
    arrivals.sort(key=lambda a: a["minutes"])
    return arrivals


def parse_routes(json_text: str) -> list[dict[str, Any]]:
    """bus.jeju.go.kr searchRouteByStationList → 정류장 경유 노선(노선번호 순, 중복 제거)."""
    routes: dict[str, dict[str, Any]] = {}
    for d in _load_list(json_text):
        route_id = str(d.get("ROUTE_ID", ""))
        if not route_id or route_id in routes:
            continue
        routes[route_id] = {
            "routeId": route_id,
            "routeNum": str(d.get("ROUTE_NUM", "")),
            "routeName": str(d.get("ROUTE_NM", "")),
            "origin": str(d.get("ORGT_NM", "")),
            "destination": str(d.get("DST_NM", "")),
        }

    def sort_key(r: dict[str, Any]) -> tuple:
        num = r["routeNum"]
        return (0, int(num), r["routeName"]) if num.isdigit() else (1, 0, num + r["routeName"])

    return sorted(routes.values(), key=sort_key)
