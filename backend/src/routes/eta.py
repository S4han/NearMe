"""내 위치 → 장소 도보·자동차 소요 시간(T map). 장소를 선택했을 때만 호출한다."""

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query

import cache
from config import ETA_TTL, KST, TMAP_APP_KEY, TMAP_CAR_URL, TMAP_PEDESTRIAN_URL, WALK_MAX_M
from http_client import UpstreamError, post_json
from services import routes
from services.jeju_bus import distance_m

router = APIRouter(prefix="/api/routes", tags=["routes"])


async def _summary(url: str, body: dict[str, Any]) -> dict[str, int] | None:
    """한 가지 수단의 경로 요약. 실패하면 None(다른 수단은 계속 보여주기 위해)."""
    try:
        return routes.parse_tmap_summary(await post_json(url, body, {"appKey": TMAP_APP_KEY}))
    except (UpstreamError, ValueError) as e:
        print(f"[routes] upstream error: {e!r}")
        return None


@router.get("/eta")
async def eta(
    from_lat: float = Query(ge=-90, le=90),
    from_lng: float = Query(ge=-180, le=180),
    to_lat: float = Query(ge=-90, le=90),
    to_lng: float = Query(ge=-180, le=180),
):
    if not TMAP_APP_KEY:
        raise HTTPException(status_code=503, detail="경로 안내 키가 설정되지 않았습니다.")
    coords = [routes.round_coord(v) for v in (from_lat, from_lng, to_lat, to_lng)]
    key = "eta:" + ",".join(map(str, coords))
    data = cache.get(key)
    if data is None:
        body = routes.request_body(*coords)
        want_walk = distance_m(*coords) <= WALK_MAX_M
        if want_walk:
            walk, car = await asyncio.gather(_summary(TMAP_PEDESTRIAN_URL, body), _summary(TMAP_CAR_URL, body))
        else:
            walk, car = None, await _summary(TMAP_CAR_URL, body)
        if walk is None and car is None:
            raise HTTPException(status_code=502, detail="경로 안내 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요.")
        data = {"walk": walk, "car": car, "fetchedAt": datetime.now(KST).isoformat(timespec="seconds")}
        # 일부 수단만 실패한 결과는 오래 남기지 않는다(다음 선택 때 다시 시도)
        if car is not None and (walk is not None or not want_walk):
            cache.set(key, data, ETA_TTL)
    return data
