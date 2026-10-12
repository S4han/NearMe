"""외부 HTTP 호출. 로컬(uvicorn)은 httpx, Cloudflare Python Workers는 JS fetch를 사용."""

import ssl

from config import UPSTREAM_TIMEOUT


class UpstreamError(Exception):
    """외부 API 호출 실패(연결 실패, 시간 초과, 오류 응답)."""


def _ssl_verify() -> ssl.SSLContext | bool:
    """OS 인증서 저장소로 검증(truststore).

    bus.jeju.go.kr은 중간 인증서를 보내지 않아 Python 기본 인증서 목록(certifi)으로는 검증에 실패한다.
    Windows/macOS 인증서 저장소는 빠진 중간 인증서를 보완해 검증하므로 truststore를 사용한다.
    검증 자체를 끄지는 않는다.
    """
    try:
        import truststore
    except ImportError:
        return True
    return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


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
        async with httpx.AsyncClient(
            timeout=UPSTREAM_TIMEOUT, follow_redirects=True, verify=_ssl_verify()
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPError as e:
        raise UpstreamError(f"{type(e).__name__}: {e} ({url})") from e
