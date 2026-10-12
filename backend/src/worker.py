"""Cloudflare Python Workers 진입점: FastAPI 앱을 Workers ASGI 어댑터로 연결.

FastAPI(OpenTelemetry)는 import 시 uuid4()로 난수를 만든다. Workers는 시작(최상위 import) 중
난수 생성을 금지하므로, FastAPI 앱은 첫 요청 처리 시점에 함수 안에서 import 한다.
"""

from workers import WorkerEntrypoint

_app = None


def _get_app():
    global _app
    if _app is None:
        from main import app

        _app = app
    return _app


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        import asgi  # Cloudflare Python Workers 런타임 제공 모듈

        js_request = getattr(request, "js_object", request)
        return await asgi.fetch(_get_app(), js_request, self.env)
