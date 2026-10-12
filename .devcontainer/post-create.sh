#!/usr/bin/env bash
# Codespace 최초 생성 시 1회 실행: Frontend/Backend 의존성 설치
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== Frontend: npm install =="
(cd frontend && npm install)

echo "== Backend: venv + pip install =="
(cd backend && python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt)

echo "== 설치 완료. README의 'GitHub Codespaces' 절을 참고해 서버를 실행하세요. =="
