"""T map 경로 안내 응답을 NearMe 표준 JSON으로 변환. 필드 정의는 docs/route-eta-api.md 참고."""

import json
from typing import Any
from urllib.parse import quote


def parse_tmap_summary(json_text: str) -> dict[str, int]:
    """T map 도보/자동차 경로 응답(GeoJSON) → {"distance": m, "seconds": 초}.

    첫 번째 feature(출발지)의 properties에 경로 전체 totalDistance·totalTime이 들어 있다.
    """
    data = json.loads(json_text)
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    if "error" in data:
        err = data["error"] if isinstance(data["error"], dict) else {}
        raise ValueError(f"T map error {err.get('code', '?')}: {err.get('message', data['error'])}")
    for feature in data.get("features") or []:
        props = feature.get("properties") if isinstance(feature, dict) else None
        if isinstance(props, dict) and "totalTime" in props and "totalDistance" in props:
            return {"distance": int(props["totalDistance"]), "seconds": int(props["totalTime"])}
    raise ValueError("T map response has no totalTime/totalDistance")


def round_coord(value: float) -> float:
    """캐시 키용 좌표 반올림(소수 4자리 ≈ 10m)."""
    return round(value, 4)


def request_body(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> dict[str, Any]:
    """T map 요청 공통 본문. X=경도, Y=위도(WGS84). 도보 API는 출발지·도착지 이름이 필수다."""
    return {
        "startX": str(from_lng),
        "startY": str(from_lat),
        "endX": str(to_lng),
        "endY": str(to_lat),
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        # 이름은 UTF-8 URL 인코딩해서 보내도록 되어 있다(T map 도보 경로 안내 명세)
        "startName": quote("출발"),
        "endName": quote("도착"),
    }
