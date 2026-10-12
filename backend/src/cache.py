"""외부 API 응답용 간단한 메모리 캐시(프로세스/Worker 인스턴스 단위)."""

import time
from typing import Any

_store: dict[str, tuple[float, Any]] = {}


def get(key: str) -> Any | None:
    item = _store.get(key)
    if item is None:
        return None
    expires_at, value = item
    if time.monotonic() >= expires_at:
        _store.pop(key, None)
        return None
    return value


def set(key: str, value: Any, ttl: float) -> None:
    _store[key] = (time.monotonic() + ttl, value)
