# 공항·항공 운항정보 API 정리

> 작성: 2026-10-12
> 분석 문서: 한국공항공사 실시간 항공기 운항정보 검색 GW OpenAPI 활용가이드 V1(2026-08-11 제정), 국토교통부(TAGO) 국내항공운항정보 서비스 활용가이드 v1.0
> (이전 한국공항공사 항공기 운항정보 OpenAPI v2.1 `openapi.airport.co.kr`은 GW로 대체되어 더 이상 사용하지 않음)
> 실측: 아직 안 함(인증키 미발급). 아래 응답 형식은 가이드 예제 기준이며 실제 응답으로 확인 필요.

## 결론: NearMe에서 사용할 API

| 기능 | 사용 API | 형식 | 인증 |
|---|---|---|---|
| 주변 공항 | Backend 내장 목록(한국공항공사 운영 국내 공항 14곳, 좌표·코드) | — | 없음 |
| 공항 실시간 출발/도착 현황 | 한국공항공사 GW `flight-search/info` | XML(`type=xml`, JSON도 지원) | data.go.kr 인증키 |
| 노선별 오늘 시간표·운임 | TAGO `getFlightOpratInfoList` | JSON(`_type=json`) | data.go.kr 인증키 |

- 두 API 모두 **공공데이터포털(data.go.kr)에서 각각 활용신청**(한국공항공사_실시간 항공기 운항정보 검색, 국토교통부_(TAGO)_국내항공운항정보)한 뒤, 발급된 일반 인증키 하나를 Backend 환경변수 `DATA_GO_KR_SERVICE_KEY`로 넣는다.
  포털의 `Encoding`/`Decoding` 키 어느 쪽을 넣어도 된다(Backend가 `%`가 있으면 원문으로 되돌린 뒤 인코딩).
- 키가 없으면 주변 공항 검색만 동작하고, 현황·시간표는 `503 항공 운항정보 인증키가 설정되지 않았습니다.`를 반환한다.
- 인천공항은 인천국제공항공사 소관이라 한국공항공사 실시간 현황에 없으므로 목록에서 제외했다.

## NearMe Backend 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/flights/airports/nearby?lat=&lng=&radius=50000&limit=5` | 주변 공항(가까운 순) |
| GET | `/api/flights/airports/{CODE}/status?direction=departure\|arrival` | 오늘 1시간 전~6시간 후 출발/도착 항공편(60초 캐시) |
| GET | `/api/flights/schedule?dep=CJU&arr=GMP&date=YYYYMMDD` | 국내선 노선 시간표·운임(30분 캐시, `date` 생략 시 오늘) |

응답 예(`status`):

```json
{"airport": {"code": "CJU", "name": "제주국제공항"}, "direction": "departure",
 "flights": [{"flightNo": "7C102", "airline": "제주항공", "direction": "departure", "counterpart": "김포",
              "counterpartCode": "GMP", "international": false, "scheduledTime": "06:00",
              "estimatedTime": "06:15", "status": "지연", "gate": "5"}],
 "fetchedAt": "2026-10-12T09:30:00+09:00"}
```

- `estimatedTime`: 변경 시각. 예정 시각과 같으면 `null`.
- `status`: 공항공사 `rmkKor` 그대로(출발, 도착, 지연, 결항, 탑승중, 마감 등). 없으면 `null`.

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
  공항 전체 현황이 목적이라 보내지 않는다. 실제 호출에서 필수 오류가 나면 편명 없이 전체를 받는 방법(빈 값 등)을 확인해야 한다.

## 2. TAGO getFlightOpratInfoList — 노선 시간표·운임

`https://apis.data.go.kr/1613000/DmstcFlightNvgInfoService/getFlightOpratInfoList` (가이드는 http, 포털은 https도 지원)

| 요청 | 의미 |
|---|---|
| `depAirportId` / `arrAirportId` | TAGO 공항ID(`NAARKPC` 제주 등, Backend `AIRPORTS.tagoId`) |
| `depPlandTime` | 출발일 `YYYYMMDD` |
| `airlineId` | 항공사ID(선택, 미사용) |
| `numOfRows` / `pageNo` / `_type` | 200 / 1 / `json` |

| 응답 필드 | 의미 | NearMe |
|---|---|---|
| `vihicleId` | 편명(필드명 오타 그대로) | `flightNo` |
| `airlineNm` | 항공사 | `airline` |
| `depPlandTime` / `arrPlandTime` | `YYYYMMDDHHMI` | `departureTime` / `arrivalTime` (`HH:MM`) |
| `economyCharge` / `prestigeCharge` | 일반석/비즈니스석 운임(원), 0이면 없음 | `economyFare` / `businessFare` (0 → `null`) |

- JSON의 `items.item`은 1건이면 객체, 여러 건이면 배열, 0건이면 `items`가 빈 문자열일 수 있어 모두 처리한다.
- 운임은 기준 운임이며 실제 판매가와 다를 수 있다(화면에 안내).

공항ID 매핑(가이드 예제 `NAARKJJ`=광주, `NAARKPC`=제주, `NAARKPS`=사천 확인, 나머지는 `getArprtList`로 실측 확인 필요):

| IATA | TAGO | 공항 | IATA | TAGO | 공항 |
|---|---|---|---|---|---|
| GMP | NAARKSS | 김포 | RSU | NAARKJY | 여수 |
| PUS | NAARKPK | 김해 | USN | NAARKPU | 울산 |
| CJU | NAARKPC | 제주 | KPO | NAARKTH | 포항경주 |
| TAE | NAARKTN | 대구 | HIN | NAARKPS | 사천 |
| CJJ | NAARKTU | 청주 | YNY | NAARKNY | 양양 |
| KWJ | NAARKJJ | 광주 | KUV | NAARKJK | 군산 |
| MWX | NAARKJB | 무안 | WJU | NAARKNW | 원주 |

## 오류 처리

- 공공데이터포털 게이트웨이 오류(인증키 미등록 `30`, 활용기간 만료 `31`, 요청 한도 초과 `22` 등)는 `_type=json`이어도 **XML**로 온다:
  `<OpenAPI_ServiceResponse><cmmMsgHeader><errMsg>SERVICE ERROR</errMsg><returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg><returnReasonCode>30</returnReasonCode>…`
- 제공기관 오류는 `header/resultCode`가 `00`이 아님(TAGO `99` INVALID_REQUEST_PARAMETER_ERROR).
- 두 경우 모두 Backend는 로그에 원인을 남기고 `502`를 반환한다. 활용신청 직후에는 키가 동기화되기까지 `30` 오류가 날 수 있다(보통 1시간 이내).

## 미검증 / 남은 확인

- [ ] 실제 인증키로 두 API 응답 형식 확인(특히 KAC GW에서 `schFln` 없이 호출 가능 여부, `numOfRows` 지원, `rmkKor` 값 종류)
- [ ] TAGO 공항ID 매핑 — `getArprtList` 응답과 대조
- [ ] Cloud Run 대만(`asia-east1`)에서 `apis.data.go.kr` 접속 가능 여부(TAGO 호스트는 Cloud Shell 대만에서 접속 확인됨)
- [ ] 자정 전후 조회 범위(현재는 오늘 00:00~23:59로 자름)
