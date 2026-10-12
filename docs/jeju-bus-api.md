# 제주 버스 API 분석 및 실측 결과

> 작성: 2026-10-12 / 실측: 사용자 PC(Windows PowerShell, `curl.exe`)
> 분석 문서: JTBIS OpenAPI 정의서 V2.0(2018), 제주데이터허브 버스 데이터셋 API 가이드 V2.0(2019)·정류소 기본정보 V1.0(2020), 제주 버스 정보 OPEN API Guide(xlsx)

## 결론: NearMe에서 사용할 API

| 기능 | 사용 API | 형식 | 인증 | 실측 |
|---|---|---|---|---|
| 주변 정류장(좌표) | `http://busopen.jeju.go.kr/OpenAPI/service/bis/Station` | XML | 없음 | ✅ 전체 4,816 / `useYn=Y` 4,352곳, 1회 응답 약 1.1MB(페이지 분할 없음) |
| 실시간 도착 예정 | `https://bus.jeju.go.kr/api/searchArrivalInfoList.do?station_id={id}` | JSON | 없음 | ✅ |
| 정류장 통과 노선 | `https://bus.jeju.go.kr/api/searchRouteByStationList.do?station_id={id}` | JSON | 없음 | ✅ |

- 세 API의 정류장 ID 형식이 같다(예: `405000153`). 제주 안에서는 Google `placeId` ↔ `stationId` 매핑이 필요 없도록 **버스 정류소 카테고리는 BIS 정류장 데이터로 검색**한다.
- `bus.jeju.go.kr`는 `http://` 요청 시 `302 → https://`로 이동한다. 처음부터 `https://`로 호출한다.
- 정류장은 반드시 `useYn=Y`만 사용한다(예: `405000155 한국병원`은 `useYn=N`).

## 1. Station (JTBIS) — 정류장 목록

`http://busopen.jeju.go.kr/OpenAPI/service/bis/Station` (선택: `?last=YYYY-MM-DD HH:MM:SS` 이후 변경분)

```xml
<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header>
<body><items>
<item><dirTp>S</dirTp><govNm>405</govNm><localX>126.514</localX><localY>33.499974</localY><mobiNum>0</mobiNum>
<stationId>405000153</stationId><stationNm>제주버스터미널</stationNm><upd>2026-07-28 09:28:44</upd><useYn>Y</useYn></item>
...
```

| 필드 | 의미 |
|---|---|
| `stationId` | 정류장 ID |
| `stationNm` | 정류장 이름 (같은 이름이 방향별로 2개 이상 존재) |
| `localX` / `localY` | 경도 / 위도 |
| `dirTp` | 방향 `N`/`S`/`E`/`W`/`null` |
| `useYn` | 사용 여부 — `Y`만 사용 |
| `upd` | 갱신 일시 (실측 2026-07-28, 현재도 갱신 중) |

- `http` 전용이므로 HTTPS 페이지(브라우저)에서 직접 호출 불가 → Backend 또는 빌드 시 정적 파일로 변환.
- 정류장은 자주 바뀌지 않으므로 하루 1회 갱신이면 충분.

## 2. searchArrivalInfoList — 실시간 도착 예정

`https://bus.jeju.go.kr/api/searchArrivalInfoList.do?station_id=405000153`

```json
[{"ARRV_STATION_ID":405000153,"ROUTE_SUB_NM":"제주버스터미널(종점)","VH_ID":7983663,"ROUTE_ID":405246101,
  "ROUTE_NUM":"461","PLATE_NO":"제주79아3663","CURR_STATION_ID":405000372,"PREDICT_TRAV_TM":19,
  "REMAIN_STATION":12,"CURR_STATION_NM":"남녕고등학교","LOW_PLATE_TP":"Y"}, ...]
```

| 필드 | 의미 |
|---|---|
| `ROUTE_NUM` / `ROUTE_SUB_NM` | 노선 번호 / 행선지 |
| `PREDICT_TRAV_TM` | 도착 예정 시간(분) |
| `REMAIN_STATION` | 남은 정류장 수 |
| `CURR_STATION_NM` | 버스의 현재(최근) 정류장 |
| `PLATE_NO` / `VH_ID` | 차량 번호 / 차량 ID |
| `LOW_PLATE_TP` | 저상버스 `Y`/`N` |

- 응답은 배열 그대로(래퍼 없음). 도착 예정 버스가 없으면 빈 배열일 것으로 예상(미검증).
- 응답에 산출 시각이 없으므로 Backend가 **조회 시각**을 함께 내려준다(마지막 갱신 시각 표시용).

## 3. searchRouteByStationList — 정류장 통과 노선

`https://bus.jeju.go.kr/api/searchRouteByStationList.do?station_id=405000153`

```json
[{"STATION_NM":"제주버스터미널","ROUTE_SUB_NM":"남원환승정류장(남원읍사무소)","ORGT_NM":"제주국제공항2(일주동로, 516도로)",
  "ROUTE_ID":405410111,"ROUTE_NUM":"101","DST_STATION_ID":406001604,"DST_NM":"남원환승정류장(남원읍사무소)",
  "ROUTE_NM":"101-11","STATION_ID":405000153,"ORGT_STATION_ID":405002101}, ...]
```

## 사용하지 않기로 한 API와 이유

| API | 이유 |
|---|---|
| JTBIS `BusArrives` | 운행 중이 아닌 노선도 `predictTravTm=0`으로 포함, `calcDate`가 과거(2025-05-08)로 고정되어 신뢰 불가. `routeId`만 있어 노선 번호 변환 필요 |
| JTBIS `StationRoutePs` | 2017년 폐지 노선(`useYn=N`)이 다수 섞여 있음 |
| 제주데이터허브 정류소/노선 기본정보 | 앱키 필요, JTBIS·bus.jeju.go.kr로 대체 가능. 단 `direction`(방면), `localInfo`(주변 안내)는 BIS에 없어 추후 보강용으로 검토 |
| 제주데이터허브 승객수 통계(일/월/시간/노선/정류소/읍면동) | 통계 데이터라 실시간 기능과 무관. "붐비는 정류장" 등 부가 기능 후보 |

## 문서와 실제의 차이 (구현 시 주의)

- JTBIS 정의서 예제의 `<time>`, `</reponse>`, `calcData` 등은 오타. 실제 응답은 `<item>`, `</response>`.
- JTBIS Station은 문서와 달리 페이지 분할 없이 전체를 한 번에 응답.
- `bus.jeju.go.kr` API는 xlsx 가이드에 작성일·제공기관·SLA 표기가 없음 → 예고 없는 변경 가능성. 장애 시 JTBIS로 대체할 수 있도록 서비스 계층을 분리한다.

## 미검증 / 남은 확인

- [ ] `bus.jeju.go.kr` 응답의 CORS 헤더(`Access-Control-Allow-Origin`) — 브라우저 직접 호출 가능 여부
- [ ] 막차 이후·운행 없는 정류장의 도착 API 응답 형태(빈 배열 여부)
- [ ] 호출 빈도 제한 여부(JTBIS 문서상 30 tps)
- [ ] Cloudflare에서 `http://busopen.jeju.go.kr` 호출 가능 여부
- [x] Cloudflare Workers `fetch`가 `bus.jeju.go.kr`의 불완전한 인증서 체인을 통과하는지 → **실패** (`pywrangler dev`, `internal error`). JTBIS 자동 전환으로 대응

## 인증서 문제 (2026-10-12 확인)

`bus.jeju.go.kr`은 TLS 핸드셰이크에서 **중간 인증서를 보내지 않는다.**
- Windows `curl.exe`(Schannel): 중간 인증서를 자동 보완 → 성공
- Python `httpx` 기본(certifi): `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate` → 실패
- 대응: `truststore`로 OS 인증서 저장소를 사용(Windows/macOS는 보완 동작). 검증을 끄지(`verify=False`) 않는다.
- Linux(Codespaces)와 Cloudflare Workers는 자동 보완이 안 될 수 있음 → 배포 단계에서 검증 필요.

## 자동 전환(Fallback) 구조 (2026-10-12)

도착 정보·경유 노선은 `bus.jeju.go.kr` → 실패 시 JTBIS 순으로 조회하고, 응답에 `source`(`bus.jeju.go.kr` 또는 `jtbis`)를 표시한다.
`bus.jeju.go.kr` 실패 후 10분간은 바로 JTBIS를 사용한다.

| 기능 | 1순위 bus.jeju.go.kr | 대체 JTBIS |
|---|---|---|
| 도착 예정 | `searchArrivalInfoList` | `BusArrives`(arrvVhId≠0만, 차량 중복 제거) + `Bus` 노선 목록으로 노선번호·행선지 변환 |
| 경유 노선 | `searchRouteByStationList` | `StationRoutePs`(useYn=Y) + `Bus`(useYn=Y) |
| JTBIS에서 빠지는 정보 | — | 버스 현재 정류장명, 차량번호, 저상 여부(`null`), 노선 출발지(`null`) |

JTBIS `Bus` 실측: 응답 형식은 문서와 동일(`routeId`, `routeNm`, `routeNum`, `routeSubNm`, `useYn` 등), 폐지 노선(`useYn=N`)도 포함.
