"""공항·항공편 데이터: 국내 공항 목록과 운항정보 API 응답을 NearMe 표준 JSON 형태로 변환.

외부 호출 없이 문자열만 다루므로 단위 테스트가 쉽다. 필드 정의는 docs/flight-api.md 참고.
- 실시간 현황: 한국공항공사 실시간 항공기 운항정보 검색 GW flight-search/info(XML)
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any

from services.jeju_bus import distance_m

# 한국공항공사(KAC) 운영 국내 공항 14곳. code: IATA(KAC API 공항코드).
# 인천공항은 인천국제공항공사 소관이라 KAC 실시간 현황에 없으므로 제외한다.
AIRPORTS: list[dict[str, Any]] = [
    {"code": "GMP", "name": "김포국제공항", "shortName": "김포", "lat": 37.5583, "lng": 126.7906},
    {"code": "PUS", "name": "김해국제공항", "shortName": "김해", "lat": 35.1795, "lng": 128.9382},
    {"code": "CJU", "name": "제주국제공항", "shortName": "제주", "lat": 33.5113, "lng": 126.4930},
    {"code": "TAE", "name": "대구국제공항", "shortName": "대구", "lat": 35.8941, "lng": 128.6589},
    {"code": "CJJ", "name": "청주국제공항", "shortName": "청주", "lat": 36.7166, "lng": 127.4991},
    {"code": "KWJ", "name": "광주공항", "shortName": "광주", "lat": 35.1264, "lng": 126.8089},
    {"code": "MWX", "name": "무안국제공항", "shortName": "무안", "lat": 34.9914, "lng": 126.3828},
    {"code": "RSU", "name": "여수공항", "shortName": "여수", "lat": 34.8423, "lng": 127.6170},
    {"code": "USN", "name": "울산공항", "shortName": "울산", "lat": 35.5935, "lng": 129.3517},
    {"code": "KPO", "name": "포항경주공항", "shortName": "포항경주", "lat": 35.9879, "lng": 129.4204},
    {"code": "HIN", "name": "사천공항", "shortName": "사천", "lat": 35.0886, "lng": 128.0704},
    {"code": "YNY", "name": "양양국제공항", "shortName": "양양", "lat": 38.0613, "lng": 128.6692},
    {"code": "KUV", "name": "군산공항", "shortName": "군산", "lat": 35.9038, "lng": 126.6158},
    {"code": "WJU", "name": "원주공항", "shortName": "원주", "lat": 37.4381, "lng": 127.9604},
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
    """KAC flight-search/info XML → (항공편 목록, totalCount)."""
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


def _flight_digits(flight_no: str) -> int:
    """편명의 숫자 자릿수(KE5242 → 4). 숫자가 없으면 크게 잡아 뒤로 보낸다."""
    digits = sum(c.isdigit() for c in flight_no[2:])
    return digits or 99


def merge_codeshares(flights: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """공동운항편(같은 비행기를 여러 항공사 편명으로 판매)을 한 줄로 합친다.

    방향·예정/변경 시각·상대 공항·게이트·상태가 모두 같으면 같은 비행기로 본다.
    게이트가 없으면 같은 시각 같은 노선의 다른 비행기일 수 있어 합치지 않는다.
    API가 실제 운항사를 알려주지 않으므로, 판매용 편명이 보통 더 길다는 점을 이용해
    숫자 자릿수가 적은 편명을 대표로 하고 나머지는 codeshares에 담는다(같으면 원래 순서).
    입력 순서(예정 시각 순)를 유지한다.
    """
    groups: dict[tuple, list[dict[str, Any]]] = {}
    order: list[tuple] = []
    for i, f in enumerate(flights):
        if f["gate"]:
            key = (
                f["direction"],
                f["scheduledTime"],
                f["estimatedTime"],
                f["counterpartCode"] or f["counterpart"],
                f["gate"],
                f["status"],
            )
        else:
            key = ("single", i)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(f)

    merged = []
    for key in order:
        group = sorted(groups[key], key=lambda f: _flight_digits(f["flightNo"]))
        primary, others = group[0], group[1:]
        merged.append(
            {**primary, "codeshares": [{"flightNo": o["flightNo"], "airline": o["airline"]} for o in others]}
        )
    return merged

