"""제주 버스 API 응답을 NearMe 표준 JSON 형태로 변환.

외부 호출 없이 문자열만 다루므로 단위 테스트가 쉽다. 필드 정의는 docs/jeju-bus-api.md 참고.
"""

import json
import math
import re
import xml.etree.ElementTree as ET
from typing import Any

DIRECTIONS = {"N", "S", "E", "W"}


def _text(item: ET.Element, tag: str) -> str:
    return (item.findtext(tag) or "").strip()


def _items(xml_text: str) -> list[ET.Element]:
    root = ET.fromstring(xml_text)
    result_code = root.findtext("./header/resultCode")
    if result_code not in (None, "00"):
        raise ValueError(f"JTBIS resultCode={result_code}")
    return list(root.iter("item"))


def parse_stations(xml_text: str) -> list[dict[str, Any]]:
    """JTBIS Station XML → 사용 중(useYn=Y)이고 실제 승하차가 가능한 정류장 목록.

    '제주버스터미널(가상정류소)', '차고지(가상)'처럼 이름에 '가상'이 들어간 시스템용 정류장은 제외한다.
    """
    stations = []
    for item in _items(xml_text):
        if _text(item, "useYn") != "Y":
            continue
        try:
            lng = float(_text(item, "localX"))
            lat = float(_text(item, "localY"))
        except ValueError:
            continue
        station_id = _text(item, "stationId")
        name = _text(item, "stationNm")
        if "가상" in name:
            continue
        if not station_id or not (-90 <= lat <= 90 and -180 <= lng <= 180):
            continue
        direction = _text(item, "dirTp").upper()
        stations.append(
            {
                "id": station_id,
                "name": name,
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


def _route_sort_key(r: dict[str, Any]) -> tuple:
    """노선번호의 앞자리 숫자 기준 정렬(43-1 < 101 < 461), 숫자가 없으면 뒤로."""
    m = re.match(r"\d+", r["routeNum"])
    return (0, int(m.group()), r["routeNum"], r["routeName"]) if m else (1, 0, r["routeNum"], r["routeName"])


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

    return sorted(routes.values(), key=_route_sort_key)


# ---- JTBIS 대체 경로 (bus.jeju.go.kr 장애 또는 Workers 인증서 문제 시) ----


def parse_bus_routes(xml_text: str) -> dict[str, dict[str, Any]]:
    """JTBIS Bus XML → {routeId: 노선 정보}. 폐지 노선도 ID 변환용으로 포함하고 inUse로 구분."""
    routes = {}
    for item in _items(xml_text):
        route_id = _text(item, "routeId")
        if not route_id:
            continue
        routes[route_id] = {
            "routeId": route_id,
            "routeNum": _text(item, "routeNum"),
            "routeName": _text(item, "routeNm"),
            "destination": _text(item, "routeSubNm"),
            "inUse": _text(item, "useYn") == "Y",
        }
    return routes


def parse_jtbis_arrivals(xml_text: str, routes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """JTBIS BusArrives XML → 도착 예정 목록(빠른 순).

    운행 중이 아닌 노선도 arrvVhId=0, predictTravTm=0으로 내려오므로 실제 차량(arrvVhId≠0)만 남긴다.
    버스의 현재 정류장명·차량번호·저상 여부는 제공되지 않는다.
    """
    seen: set[tuple[str, str]] = set()
    arrivals = []
    for item in _items(xml_text):
        vehicle_id = _text(item, "arrvVhId")
        route_id = _text(item, "routeId")
        minutes = _int(_text(item, "predictTravTm"))
        if vehicle_id in ("", "0") or minutes is None or (route_id, vehicle_id) in seen:
            continue
        seen.add((route_id, vehicle_id))
        route = routes.get(route_id, {})
        arrivals.append(
            {
                "routeId": route_id,
                "routeNum": route.get("routeNum") or route_id,
                "destination": route.get("destination", ""),
                "minutes": minutes,
                "remainStations": _int(_text(item, "leftStation")),
                "currentStationName": None,
                "plateNo": None,
                "lowFloor": None,
            }
        )
    arrivals.sort(key=lambda a: a["minutes"])
    return arrivals


def parse_jtbis_station_routes(xml_text: str, routes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """JTBIS StationRoutePs XML → 정류장 경유 노선(사용 중인 노선만, 노선번호 순)."""
    found: dict[str, dict[str, Any]] = {}
    for item in _items(xml_text):
        route_id = _text(item, "routeId")
        route = routes.get(route_id)
        if _text(item, "useYn") != "Y" or not route or not route["inUse"] or route_id in found:
            continue
        found[route_id] = {
            "routeId": route_id,
            "routeNum": route["routeNum"],
            "routeName": route["routeName"],
            "origin": None,
            "destination": route["destination"],
        }
    return sorted(found.values(), key=_route_sort_key)
