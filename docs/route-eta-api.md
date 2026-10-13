# 소요 시간(도보·자동차) — T map 경로 안내

> 작성: 2026-10-13 · 실측: 아직 안 함(앱 키 발급 후 확인 필요)

## 왜 T map인가

Google 지도는 한국에서 도보·자동차 길찾기를 제공하지 않는다(대중교통만). 그래서 실제 경로 기준 소요 시간은
SK open API의 **T map 경로 안내**를 Backend에서 호출해 구한다.

## NearMe Backend 엔드포인트

`GET /api/routes/eta?from_lat=&from_lng=&to_lat=&to_lng=`

```json
{"walk": {"distance": 1234, "seconds": 925}, "car": {"distance": 1630, "seconds": 372}, "fetchedAt": "2026-10-13T11:48:51+09:00"}
```

- 화면에서 **장소를 선택했을 때만** 호출한다(내 위치 → 선택 장소). 목록 전체를 계산하지 않아 호출 수가 적다.
- 도보는 직선거리 10km 이내일 때만 조회한다(그보다 멀면 `walk: null`).
- 좌표를 소수 4자리(약 10m)로 반올림해 10분간 캐시한다. 한쪽 수단만 실패한 결과는 캐시하지 않는다.
- 키(`TMAP_APP_KEY`)가 없으면 `503`, 두 수단 모두 실패하면 `502`. 화면은 이 경우 소요 시간 줄을 숨긴다.

## 사용하는 T map API

| 수단 | 요청 | 응답에서 쓰는 값 |
|---|---|---|
| 도보 | `POST https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1` | 첫 feature의 `properties.totalDistance`(m), `totalTime`(초) |
| 자동차 | `POST https://apis.openapi.sk.com/tmap/routes?version=1` | 같음 |

- 헤더 `appKey: <TMAP_APP_KEY>`, JSON 본문 `startX/startY/endX/endY`(X=경도, Y=위도), `reqCoordType`·`resCoordType`=`WGS84GEO`.
- 도보는 `startName`·`endName`이 필수(UTF-8 URL 인코딩).

## 키 발급·등록

1. SK open API(openapi.sk.com)에서 앱을 만들고 **T map** 상품(경로 안내: 보행자·자동차)을 사용 신청 → `appKey` 발급
2. 로컬: `export TMAP_APP_KEY='앱키'` / Cloud Run: `gcloud run services update nearme-api --region asia-east1 --update-env-vars TMAP_APP_KEY=앱키`

## 미검증

- [ ] 실제 키로 도보·자동차 응답 형식 확인(특히 오류 응답 형태)
- [ ] Cloud Run 대만(`asia-east1`)에서 `apis.openapi.sk.com` 접속 가능 여부
- [ ] 무료 사용량 한도와 초과 시 응답
