"""외부 HTTP 호출. 로컬(uvicorn)은 httpx, Cloudflare Python Workers는 JS fetch를 사용."""

from config import UPSTREAM_TIMEOUT


class UpstreamError(Exception):
    """외부 API 호출 실패(연결 실패, 시간 초과, 오류 응답)."""


async def fetch_text(url: str) -> str:
    try:
        from js import fetch as js_fetch  # Cloudflare Python Workers(Pyodide)에서만 존재
    except ImportError:
        js_fetch = None

    if js_fetch is not None:
        try:
            resp = await js_fetch(url)
        except Exception as e:  # noqa: BLE001 - JS 쪽 예외 형식이 다양함
            raise UpstreamError(f"fetch failed: {e} ({url})") from e
        if not resp.ok:
            raise UpstreamError(f"HTTP {resp.status}: {url}")
        return await resp.text()

    import httpx

    try:
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPError as e:
        raise UpstreamError(f"{type(e).__name__}: {e} ({url})") from e
