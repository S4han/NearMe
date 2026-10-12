import os
import sys

# src 폴더를 import 기준으로 사용(`uvicorn src.main:app`으로 실행)
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


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "NearMe Backend"}


app.include_router(bus.router)
