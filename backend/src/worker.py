"""Cloudflare Python Workers 진입점: FastAPI 앱을 Workers ASGI 어댑터로 연결."""

import asgi  # Cloudflare Python Workers 런타임 제공 모듈

from main import app

if hasattr(asgi, "entrypoint"):
    Default = asgi.entrypoint(app)
else:
    from workers import WorkerEntrypoint

    class Default(WorkerEntrypoint):
        async def fetch(self, request):
            return await asgi.fetch(app, request.js_object, self.env)
