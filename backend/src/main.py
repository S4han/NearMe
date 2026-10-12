import os
import sys

# src 폴더를 import 기준으로 사용(로컬 `uvicorn src.main:app` / Cloudflare Workers 공용)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from config import ALLOWED_ORIGINS  # noqa: E402
from routes import bus  # noqa: E402

app = FastAPI(title="NearMe Backend", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# Cloudflare Python Workers(Pyodide)는 스레드를 지원하지 않는다.
# FastAPI는 일반 def 경로를 스레드풀에서 실행하므로 모든 경로는 async def로 작성한다.
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "NearMe Backend"}


app.include_router(bus.router)
