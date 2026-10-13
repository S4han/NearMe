# NearMe

GPS 위치 또는 지도 중심을 기준으로 주변 장소(맛집·카페·편의점·주차장·병원·버스 정류소·공항·관광지)와 교통정보를 찾는 모바일 웹앱.

| 영역 | 기술 |
|---|---|
| Frontend | React + TypeScript + Vite + Tailwind CSS (`frontend/`) |
| Backend | Python + FastAPI, 로컬은 Uvicorn (`backend/`) |
| 배포 | Frontend: Cloudflare Workers(정적 자산) / Backend: Google Cloud Run(대만 `asia-east1`) |

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

## Backend API

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/health` | 상태 확인 |
| GET | `/api/bus/stations/nearby?lat=&lng=&radius=1000&limit=20` | 제주 주변 버스 정류장(가까운 순) |
| GET | `/api/bus/stations/{stationId}/arrivals` | 실시간 도착 예정(20초 캐시) |
| GET | `/api/bus/stations/{stationId}/routes` | 정류장 경유 노선(1시간 캐시) |
| GET | `/api/flights/airports/nearby?lat=&lng=&radius=50000` | 주변 공항(가까운 순, 키 불필요) |
| GET | `/api/flights/airports/{CODE}/status?direction=departure` | 공항 실시간 출발/도착 현황(1분 캐시) |

데이터 출처와 응답 필드는 [`docs/jeju-bus-api.md`](docs/jeju-bus-api.md), [`docs/flight-api.md`](docs/flight-api.md) 참고.

### 항공 운항정보 인증키

공항 실시간 현황은 공공데이터포털(data.go.kr) 인증키가 필요합니다. 포털에서 **한국공항공사_실시간 항공기 운항정보 검색**을 활용신청한 뒤, 발급된 일반 인증키를 환경변수로 넣습니다(저장소에 커밋하지 않음). 키가 없어도 나머지 기능과 주변 공항 검색은 동작합니다.

```powershell
# 로컬(PowerShell): Backend를 실행할 터미널에서
$env:DATA_GO_KR_SERVICE_KEY = "발급받은 인증키"
```

Backend 테스트(PowerShell, `backend` 폴더):

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
```

## Backend 배포 (Google Cloud Run, 대만)

Cloudflare Python Workers 무료 플랜은 요청당 CPU 약 10ms 제한으로 FastAPI 실행이 불가(`Error 1102`, 2026-10-12 확인)하여 Cloud Run으로 배포한다.
서울 리전(`asia-northeast3`)은 제주 버스 서버 접속이 시간 초과로 실패하여 **대만 리전(`asia-east1`)** 을 사용한다.

- 운영 주소: `https://nearme-api-746950529425.asia-east1.run.app`

Google Cloud 콘솔 오른쪽 위 **Cloud Shell**(브라우저 터미널)에서:

```bash
git clone -b claude/new-session-f23yq3 https://github.com/S4han/NearMe.git   # 처음 한 번
cd NearMe && git pull

gcloud run deploy nearme-api \
  --source backend \
  --region asia-east1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --memory 512Mi
```

- 항공 운항정보 인증키는 처음 한 번 등록한다(이후 배포에도 유지됨):
  `gcloud run services update nearme-api --region asia-east1 --update-env-vars DATA_GO_KR_SERVICE_KEY=발급받은_인증키`

- 배포가 끝나면 표시되는 `Service URL`을 Cloudflare Frontend 빌드 변수 `VITE_API_BASE_URL`에 등록한다.
- `--min-instances 0`: 요청이 없으면 0대로 줄어 비용이 들지 않는다(대신 첫 요청이 1~3초 느릴 수 있음).
- `--max-instances 2`: 비정상 트래픽에도 비용이 커지지 않도록 상한을 둔다.

## Frontend 배포 (Cloudflare Workers)

- `claude/new-session-f23yq3`에 병합하면 Cloudflare가 자동으로 빌드·배포한다(빌드 변수 `VITE_API_BASE_URL`, `VITE_GOOGLE_MAPS_API_KEY`는 Cloudflare 설정에 등록).
- 직접 `npx wrangler deploy` 하지 않는다. 자동 배포된 최신 버전을 예전 코드로 덮어쓸 수 있다.
- PR 미리보기 빌드(`Workers Builds: nearme`)는 0초 만에 실패하는 경우가 있으나 운영 배포와 무관하다.
- 병합 후 배포 탭에 해당 `Merge pull request` 빌드가 없으면(GitHub 알림 누락) 배포 브랜치에 새 커밋이 들어갈 때 함께 배포된다.
- 배포 단계에서 Cloudflare API `504 Gateway Timeout`으로 실패하면 배포 탭에서 다시 시도한다.

## 배포용 빌드

```powershell
cd C:\Projects\NearMe\frontend
npm run build   # 타입 검사 + dist/ 생성
```
