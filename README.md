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

## GitHub Codespaces (브라우저에서 개발)

1. GitHub 저장소 → **Code** → **Codespaces** 탭 → **Create codespace on `<브랜치>`**
2. 처음 생성 시 `.devcontainer/post-create.sh`가 `npm install`과 Python 가상환경 설치를 자동 실행합니다(수 분 소요).
3. Codespaces 터미널은 **Linux bash**입니다. 터미널 2개를 열어 실행합니다.

**터미널 A — Backend**

```bash
cd backend
.venv/bin/python -m uvicorn src.main:app --reload --port 8000
```

**터미널 B — Frontend**

```bash
cd frontend
npm run dev
```

- 5173 포트가 자동 전달되어 브라우저 탭이 열립니다(안 열리면 **PORTS** 탭에서 5173의 지구본 아이콘 클릭).
- Frontend의 `/api` 요청은 Codespace 내부에서 8000번으로 프록시되므로 8000 포트를 공개할 필요가 없습니다.
- 사용하지 않을 때는 Codespace를 **Stop** 하세요. 무료 사용 시간/저장공간을 초과하면 과금될 수 있습니다.

## 배포용 빌드

```powershell
cd C:\Projects\NearMe\frontend
npm run build   # 타입 검사 + dist/ 생성
```
