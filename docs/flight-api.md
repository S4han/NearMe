# 공항·항공 운항정보 API 정리

> 작성: 2026-10-12
> 분석 문서: 한국공항공사 실시간 항공기 운항정보 검색 GW OpenAPI 활용가이드 V1(2026-08-11 제정)
> (이전 한국공항공사 항공기 운항정보 OpenAPI v2.1 `openapi.airport.co.kr`은 GW로 대체되어 더 이상 사용하지 않음)
> 활용신청: 2026-10-13 완료(한국공항공사_실시간 항공기 운항정보 검색). TAGO 국내항공운항정보는 사용하지 않기로 함.
> 실측: 2026-10-13 Codespaces에서 `schAirCode=CJU&schIOType=O&schStTime=0800&schEdTime=1200&numOfRows=5` 호출 성공(`totalCount` 83). 아래 응답 형식은 가이드 예제 기준이며 실제 응답으로 확인 필요.

## 결론: NearMe에서 사용할 API

| 기능 | 사용 API | 형식 | 인증 |
|---|---|---|---|
| 주변 공항 | Backend 내장 목록(한국공항공사 운영 국내 공항 14곳, 좌표·코드) | — | 없음 |
| 공항 실시간 출발/도착 현황 | 한국공항공사 GW `flight-search/info` | XML(`type=xml`, JSON도 지원) | data.go.kr 인증키 |

- **공공데이터포털(data.go.kr)에서 한국공항공사_실시간 항공기 운항정보 검색을 활용신청**한 뒤, 발급된 일반 인증키 하나를 Backend 환경변수 `DATA_GO_KR_SERVICE_KEY`로 넣는다.
  포털의 `Encoding`/`Decoding` 키 어느 쪽을 넣어도 된다(Backend가 `%`가 있으면 원문으로 되돌린 뒤 인코딩).
- 키가 없으면 주변 공항 검색만 동작하고, 실시간 현황은 `503 항공 운항정보 인증키가 설정되지 않았습니다.`를 반환한다.
- 인천공항은 인천국제공항공사 소관이라 한국공항공사 실시간 현황에 없으므로 목록에서 제외했다.

## NearMe Backend 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/flights/airports/nearby?lat=&lng=&radius=50000&limit=5` | 주변 공항(가까운 순) |
| GET | `/api/flights/airports/{CODE}/status?direction=departure\|arrival` | 오늘 1시간 전~6시간 후 출발/도착 항공편(60초 캐시) |

응답 예(`status`):

```json
{"airport": {"code": "CJU", "name": "제주국제공항"}, "direction": "departure",
 "flights": [{"flightNo": "7C102", "airline": "제주항공", "direction": "departure", "counterpart": "김포",
              "counterpartCode": "GMP", "international": false, "scheduledTime": "06:00",
              "estimatedTime": "06:15", "status": "지연", "gate": "5",
              "codeshares": [{"flightNo": "KE5102", "airline": "대한항공"}]}],
 "fetchedAt": "2026-10-12T09:30:00+09:00"}
```

- `estimatedTime`: 변경 시각. 예정 시각과 같으면 `null`.
- `status`: 공항공사 `rmkKor` 그대로(출발, 도착, 지연, 결항, 탑승중, 마감 등). 없으면 `null`.
- `codeshares`: 같은 비행기의 공동운항 편명. 방향·예정/변경 시각·상대 공항·게이트·상태가 모두 같으면 한 줄로 합친다
  (실측 예: 진에어 LJ472 = 대한항공 KE5242). 게이트가 없으면 다른 비행기일 수 있어 합치지 않는다.
  API가 실제 운항사를 알려주지 않으므로 숫자 자릿수가 적은 편명을 대표로 둔다(판매용 편명이 보통 4자리) — 추정이며 틀릴 수 있다.

## 1. 한국공항공사 실시간 항공기 운항정보 검색 GW — 실시간 현황

`https://apis.data.go.kr/B551178/flight-search/info` (2026-07-06 개시, https, XML/JSON)

| 요청 | 의미 | NearMe 사용 |
|---|---|---|
| `serviceKey` | 인증키(필수) | 환경변수 |
| `pageNo` / `numOfRows` | 페이지 / 페이지당 건수(가이드 요청 명세엔 없고 응답에만 있음, 포털 공통) | 1부터 `totalCount`까지 최대 5페이지 / 100 |
| `type` | 응답 형식 `xml`/`json` | `xml` |
| `schFln` | 편명(가이드상 **필수**) | 보내지 않음 — 아래 주의 참고 |
| `schAirCode` | 기준 공항 코드(IATA) | 선택한 공항 |
| `schIOType` | `I` 도착 / `O` 출발 | 탭 |
| `schLineType` | `D` 국내 / `I` 국제 | 생략(둘 다) |
| `schStTime` / `schEdTime` | 조회 시작/끝 시각 `HHMM` | 지금-1시간 ~ 지금+6시간, 오늘 범위로 자름 |

| 응답 필드 | 의미 | NearMe |
|---|---|---|
| `airFln` | 편명 | `flightNo` |
| `airlineKorean` / `airlineEnglish` | 항공사 | `airline` |
| `boardingKor` / `arrivedKor` | 출발/도착 공항명 | 상대 공항 `counterpart` |
| `city` | 운항구간(상대 공항) 코드 | `counterpartCode` |
| `io` | `I` 도착 / `O` 출발 | `direction` |
| `line` | `국내` / `국제` | `international` |
| `std` / `etd` | 예정 / 변경 시각 `HHMM` | `scheduledTime` / `estimatedTime` |
| `rmkKor` | 항공편 상태 | `status` |
| `gate` | 게이트(비어 있으면 `<gate/>`) | `gate` |

- 응답 필드는 이전 API(`getFlightStatusList`)와 같아 변환 코드는 그대로 쓴다. 응답 맨 앞의 `<script/>` 요소는 무시된다.
- **주의 `schFln`:** 가이드는 필수로 표기하지만 예제 응답은 요청한 편명(KE1814)·공항(GMP)과 무관한 전체 목록(`totalCount` 1740)이다.
  공항 전체 현황이 목적이라 보내지 않는다. → **실측 확인: `schFln` 없이 호출해도 정상(`resultCode` 00)이며, `schAirCode`·`schIOType`·시간 조건이 모두 적용된 목록이 온다.**
- 실측 응답에는 `<script/>`가 없었고, 게이트는 `1A`처럼 문자가 섞일 수 있다(문자열로 처리).

## 오류 처리

- 공공데이터포털 게이트웨이 오류(인증키 미등록 `30`, 활용기간 만료 `31`, 요청 한도 초과 `22` 등)는 `type=json`이어도 **XML**로 온다:
  `<OpenAPI_ServiceResponse><cmmMsgHeader><errMsg>SERVICE ERROR</errMsg><returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg><returnReasonCode>30</returnReasonCode>…`
- 제공기관 오류는 `header/resultCode`가 `00`이 아님.
- 두 경우 모두 Backend는 로그에 원인을 남기고 `502`를 반환한다. 활용신청 직후에는 키가 동기화되기까지 `30` 오류가 날 수 있다(보통 1시간 이내).

## 미검증 / 남은 확인

- [x] 실제 인증키로 응답 형식 확인: `schFln` 없이 호출 가능, `numOfRows` 지원, 해외(Codespaces)에서 접속 가능
- [ ] `rmkKor` 값 종류(실측: `출발`) — 지연·결항·탑승중 등은 추가 확인
- [ ] Cloud Run 대만(`asia-east1`)에서 `apis.data.go.kr` 접속 가능 여부(같은 호스트의 다른 API는 Cloud Shell 대만에서 접속 확인됨)
- [ ] 자정 전후 조회 범위(현재는 오늘 00:00~23:59로 자름)
