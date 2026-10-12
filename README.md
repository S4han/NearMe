# NearMe

GPS 위치 또는 지도 중심을 기준으로 주변 장소(맛집·카페·주차장·병원·버스 정류소·관광지)와 교통정보를 찾는 모바일 웹앱.

| 영역 | 기술 |
|---|---|
| Frontend | React + TypeScript + Vite + Tailwind CSS (`frontend/`) |
| Backend | Python + FastAPI, 로컬은 Uvicorn (`backend/`) |
| 배포(예정) | Cloudflare Pages / Cloudflare Python Workers |

## 최초 설정 (Windows PowerShell, 1회)

Node.js 20.19 이상, Python 3.11 이상이 필요합니다.

```powershell
cd C:\Projects
git clone https://github.com/S4han/NearMe.git
cd NearMe

# Frontend 의존성
cd .\frontend
npm install

# Backend 가상환경
cd ..\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 매일 개발 시작

**터미널 A — Backend**

```powershell
cd C:\Projects\NearMe\backend
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload --port 8000
```

- `http://127.0.0.1:8000/api/health` → `{"status":"ok","service":"NearMe Backend"}`
- `http://127.0.0.1:8000/docs` → API 문서

**터미널 B — Frontend**

```powershell
cd C:\Projects\NearMe\frontend
npm run dev
```

- 터미널에 표시된 `Local` 주소(보통 `http://localhost:5173/`)로 접속
- `/api` 요청은 Vite 개발 프록시가 `127.0.0.1:8000`으로 전달합니다(개발 전용).

종료는 각 터미널에서 **Ctrl + C**.

## 배포용 빌드

```powershell
cd C:\Projects\NearMe\frontend
npm run build   # 타입 검사 + dist/ 생성
```
