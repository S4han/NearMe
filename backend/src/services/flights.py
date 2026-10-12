"""공항·항공편 데이터: 국내 공항 목록과 운항정보 API 응답을 NearMe 표준 JSON 형태로 변환.

외부 호출 없이 문자열만 다루므로 단위 테스트가 쉽다. 필드 정의는 docs/flight-api.md 참고.
- 실시간 현황: 한국공항공사 getFlightStatusList(XML)
- 스케줄·운임: TAGO 국내항공운항정보 getFlightOpratInfoList(JSON)
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any

from services.jeju_bus import distance_m

# 한국공항공사(KAC) 운영 국내 공항 14곳. code: IATA(KAC API), tagoId: TAGO 공항ID.
# 인천공항은 인천국제공항공사 소관이라 KAC 실시간 현황에 없으므로 제외한다.
AIRPORTS: list[dict[str, Any]] = [
    {"code": "GMP", "tagoId": "NAARKSS", "name": "김포국제공항", "shortName": "김포", "lat": 37.5583, "lng": 126.7906},
    {"code": "PUS", "tagoId": "NAARKPK", "name": "김해국제공항", "shortName": "김해", "lat": 35.1795, "lng": 128.9382},
    {"code": "CJU", "tagoId": "NAARKPC", "name": "제주국제공항", "shortName": "제주", "lat": 33.5113, "lng": 126.4930},
    {"code": "TAE", "tagoId": "NAARKTN", "name": "대구국제공항", "shortName": "대구", "lat": 35.8941, "lng": 128.6589},
    {"code": "CJJ", "tagoId": "NAARKTU", "name": "청주국제공항", "shortName": "청주", "lat": 36.7166, "lng": 127.4991},
    {"code": "KWJ", "tagoId": "NAARKJJ", "name": "광주공항", "shortName": "광주", "lat": 35.1264, "lng": 126.8089},
    {"code": "MWX", "tagoId": "NAARKJB", "name": "무안국제공항", "shortName": "무안", "lat": 34.9914, "lng": 126.3828},
    {"code": "RSU", "tagoId": "NAARKJY", "name": "여수공항", "shortName": "여수", "lat": 34.8423, "lng": 127.6170},
    {"code": "USN", "tagoId": "NAARKPU", "name": "울산공항", "shortName": "울산", "lat": 35.5935, "lng": 129.3517},
    {"code": "KPO", "tagoId": "NAARKTH", "name": "포항경주공항", "shortName": "포항경주", "lat": 35.9879, "lng": 129.4204},
    {"code": "HIN", "tagoId": "NAARKPS", "name": "사천공항", "shortName": "사천", "lat": 35.0886, "lng": 128.0704},
    {"code": "YNY", "tagoId": "NAARKNY", "name": "양양국제공항", "shortName": "양양", "lat": 38.0613, "lng": 128.6692},
    {"code": "KUV", "tagoId": "NAARKJK", "name": "군산공항", "shortName": "군산", "lat": 35.9038, "lng": 126.6158},
    {"code": "WJU", "tagoId": "NAARKNW", "name": "원주공항", "shortName": "원주", "lat": 37.4381, "lng": 127.9604},
]
AIRPORTS_BY_CODE = {a["code"]: a for a in AIRPORTS}


def find_nearby_airports(lat: float, lng: float, radius: float, limit: int) -> list[dict[str, Any]]:
    """반경 안의 공항을 가까운 순으로 최대 limit개."""
    found = []
    for a in AIRPORTS:
        d = distance_m(lat, lng, a["lat"], a["lng"])
        if d <= radius:
            found.append({**a, "distance": round(d)})
    found.sort(key=lambda a: a["distance"])
    return found[:limit]


def status_window(now: datetime, before_min: int = 60, after_min: int = 6 * 60) -> tuple[str, str]:
    """실시간 현황 조회 시간대(HHMM). 오늘 안으로 자른다(API가 당일 현황만 제공)."""
    start = now - timedelta(minutes=before_min)
    end = now + timedelta(minutes=after_min)
    start_hhmm = "0000" if start.date() < now.date() else start.strftime("%H%M")
    end_hhmm = "2359" if end.date() > now.date() else end.strftime("%H%M")
    return start_hhmm, end_hhmm


def _text(item: ET.Element, tag: str) -> str:
    return (item.findtext(tag) or "").strip()


def _hhmm(value: str) -> str | None:
    """'0605' → '06:05'. 형식이 다르면 None."""
    value = value.strip()
    if len(value) != 4 or not value.isdigit():
        return None
    return f"{value[:2]}:{value[2:]}"


def _check_portal_error(root: ET.Element) -> None:
    """공공데이터포털 게이트웨이 오류(XML 전용) 또는 제공기관 resultCode≠00이면 ValueError."""
    if root.tag == "OpenAPI_ServiceResponse":
        reason = root.findtext(".//returnAuthMsg") or root.findtext(".//errMsg") or "SERVICE ERROR"
        code = root.findtext(".//returnReasonCode") or "?"
        raise ValueError(f"data.go.kr error {code}: {reason.strip()}")
    result_code = root.findtext("./header/resultCode")
    if result_code not in (None, "00"):
        raise ValueError(f"resultCode={result_code}: {(root.findtext('./header/resultMsg') or '').strip()}")


def parse_flight_status(xml_text: str) -> tuple[list[dict[str, Any]], int]:
    """KAC getFlightStatusList XML → (항공편 목록, totalCount)."""
    root = ET.fromstring(xml_text)
    _check_portal_error(root)
    flights = []
    for item in root.iter("item"):
        flight_no = _text(item, "airFln")
        scheduled = _hhmm(_text(item, "std"))
        if not flight_no or not scheduled:
            continue
        io = _text(item, "io").upper()
        changed = _hhmm(_text(item, "etd"))
        flights.append(
            {
                "flightNo": flight_no,
                "airline": _text(item, "airlineKorean") or _text(item, "airlineEnglish"),
                "direction": "arrival" if io == "I" else "departure",
                # 출발편은 도착지, 도착편은 출발지가 상대 공항
                "counterpart": _text(item, "boardingKor" if io == "I" else "arrivedKor"),
                "counterpartCode": _text(item, "city") or None,
                "international": _text(item, "line") == "국제",
                "scheduledTime": scheduled,
                "estimatedTime": changed if changed != scheduled else None,
                "status": _text(item, "rmkKor") or None,
                "gate": _text(item, "gate") or None,
            }
        )
    try:
        total = int(root.findtext(".//body/totalCount") or len(flights))
    except ValueError:
        total = len(flights)
    return flights, total


def sort_flights(flights: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """예정 시각 순 정렬. 여러 페이지를 합칠 때 겹친 같은 편(방향·편명·예정시각)은 한 번만 남긴다."""
    seen: set[tuple[str, str, str]] = set()
    result = []
    for f in sorted(flights, key=lambda f: (f["scheduledTime"], f["flightNo"])):
        key = (f["direction"], f["flightNo"], f["scheduledTime"])
        if key in seen:
            continue
        seen.add(key)
        result.append(f)
    return result


def _as_list(value: Any) -> list[dict[str, Any]]:
    """TAGO JSON의 item은 1건이면 객체, 여러 건이면 배열, 0건이면 items가 빈 문자열."""
    if isinstance(value, list):
        return [v for v in value if isinstance(v, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _plan_time(value: Any) -> str | None:
    """202012010820 → '08:20'."""
    s = str(value or "").strip()
    if len(s) != 12 or not s.isdigit():
        return None
    return f"{s[8:10]}:{s[10:12]}"


def _charge(value: Any) -> int | None:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def parse_tago_schedule(text: str) -> list[dict[str, Any]]:
    """TAGO getFlightOpratInfoList JSON → 운항 스케줄(출발 시각 순).

    서비스키 오류 등은 JSON 요청이어도 XML로 응답하므로 함께 처리한다.
    """
    stripped = text.lstrip()
    if stripped.startswith("<"):
        _check_portal_error(ET.fromstring(stripped))
        raise ValueError("unexpected XML response")
    data = json.loads(text)
    response = data.get("response", {}) if isinstance(data, dict) else {}
    code = str(response.get("header", {}).get("resultCode", ""))
    if code not in ("", "00"):
        raise ValueError(f"TAGO resultCode={code}: {response.get('header', {}).get('resultMsg', '')}")
    items = response.get("body", {}).get("items")
    raw = _as_list(items.get("item") if isinstance(items, dict) else None)
    flights = []
    for d in raw:
        dep = _plan_time(d.get("depPlandTime"))
        if not dep:
            continue
        flights.append(
            {
                "flightNo": str(d.get("vihicleId", "")),  # API 필드명 오타(vihicle) 그대로
                "airline": str(d.get("airlineNm", "")),
                "departureTime": dep,
                "arrivalTime": _plan_time(d.get("arrPlandTime")),
                "economyFare": _charge(d.get("economyCharge")),
                "businessFare": _charge(d.get("prestigeCharge")),
            }
        )
    flights.sort(key=lambda f: (f["departureTime"], f["flightNo"]))
    return flights
