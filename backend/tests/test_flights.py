"""공항·항공편 응답 변환 테스트. 샘플은 한국공항공사 운항정보 OpenAPI v2.1, TAGO 국내항공운항정보 v1.0 활용가이드 예제 기반.

실행: backend 폴더에서 `python -m unittest discover tests`
"""

import json
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import KST  # noqa: E402
from services import flights  # noqa: E402

# KAC getFlightStatusList: 가이드 예제(김해 국제선 도착) + 국내선 출발편, 페이지 경계 중복 항목
STATUS_XML = """<?xml version="1.0" encoding="UTF-8"?><response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items>
<item><airFln>LJ074</airFln><airlineEnglish>JINAIR</airlineEnglish><airlineKorean>진에어</airlineKorean><airport>PUS</airport><arrivedEng>GIMHAE</arrivedEng><arrivedKor>부산/김해</arrivedKor><boardingEng>DANANG</boardingEng><boardingKor>다낭</boardingKor><city>DAD</city><etd>0619</etd><gate>5</gate><io>I</io><line>국제</line><rmkEng>ARRIVED </rmkEng><rmkKor>도착</rmkKor><std>0605</std></item>
<item><airFln>7C102</airFln><airlineEnglish>JEJU AIR</airlineEnglish><airlineKorean>제주항공</airlineKorean><airport>PUS</airport><arrivedEng>JEJU</arrivedEng><arrivedKor>제주</arrivedKor><boardingEng>GIMHAE</boardingEng><boardingKor>부산/김해</boardingKor><city>CJU</city><etd>0600</etd><io>O</io><line>국내</line><rmkEng>DEPARTED</rmkEng><rmkKor>출발</rmkKor><std>0600</std></item>
<item><airFln>BX8101</airFln><airlineKorean>에어부산</airlineKorean><arrivedKor>제주</arrivedKor><boardingKor>부산/김해</boardingKor><city>CJU</city><io>O</io><line>국내</line><std>0550</std></item>
<item><airFln>7C102</airFln><airlineKorean>제주항공</airlineKorean><arrivedKor>제주</arrivedKor><io>O</io><line>국내</line><std>0600</std></item>
<item><airFln></airFln><std>0700</std></item>
</items><numOfRows>10</numOfRows><pageNo>1</pageNo><totalCount>105</totalCount></body></response>"""

# 공공데이터포털 게이트웨이 오류(인증키 미등록) — XML로만 응답
PORTAL_ERROR_XML = """<OpenAPI_ServiceResponse><cmmMsgHeader><errMsg>SERVICE ERROR</errMsg><returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg><returnReasonCode>30</returnReasonCode></cmmMsgHeader></OpenAPI_ServiceResponse>"""


def tago_json(item):
    return json.dumps(
        {
            "response": {
                "header": {"resultCode": "00", "resultMsg": "NORMAL SERVICE."},
                "body": {"items": item, "numOfRows": 10, "pageNo": 1, "totalCount": 2},
            }
        },
        ensure_ascii=False,
    )


TAGO_ITEMS = [
    {"airlineNm": "대한항공", "arrAirportNm": "제주", "arrPlandTime": 202012011020, "depAirportNm": "광주", "depPlandTime": 202012010935, "economyCharge": 64900, "prestigeCharge": 0, "vihicleId": "KE1903"},
    {"airlineNm": "아시아나항공", "arrAirportNm": "제주", "arrPlandTime": 202012010905, "depAirportNm": "광주", "depPlandTime": 202012010820, "economyCharge": 57900, "prestigeCharge": 0, "vihicleId": "OZ8141"},
]


class AirportsTest(unittest.TestCase):
    def test_codes_unique_and_tago_ids(self):
        codes = [a["code"] for a in flights.AIRPORTS]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(flights.AIRPORTS_BY_CODE["CJU"]["tagoId"], "NAARKPC")
        self.assertEqual(flights.AIRPORTS_BY_CODE["KWJ"]["tagoId"], "NAARKJJ")

    def test_nearby_from_jeju_city_hall(self):
        found = flights.find_nearby_airports(33.4996, 126.5312, 50000, 5)
        self.assertEqual([a["code"] for a in found], ["CJU"])
        self.assertTrue(3000 < found[0]["distance"] < 5000)

    def test_nearby_sorted_and_limited(self):
        # 광주 시내: 광주공항이 무안공항보다 가깝다
        found = flights.find_nearby_airports(35.16, 126.85, 100000, 5)
        self.assertEqual([a["code"] for a in found][:2], ["KWJ", "MWX"])
        self.assertEqual(len(flights.find_nearby_airports(35.16, 126.85, 300000, 2)), 2)


class StatusWindowTest(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(flights.status_window(datetime(2026, 10, 12, 9, 30, tzinfo=KST)), ("0830", "1530"))

    def test_clamped_to_today(self):
        self.assertEqual(flights.status_window(datetime(2026, 10, 12, 0, 20, tzinfo=KST))[0], "0000")
        self.assertEqual(flights.status_window(datetime(2026, 10, 12, 21, 0, tzinfo=KST)), ("2000", "2359"))


class ParseFlightStatusTest(unittest.TestCase):
    def test_fields(self):
        items, total = flights.parse_flight_status(STATUS_XML)
        self.assertEqual(total, 105)
        self.assertEqual(len(items), 4)  # 편명 없는 항목 제외
        self.assertEqual(
            items[0],
            {
                "flightNo": "LJ074",
                "airline": "진에어",
                "direction": "arrival",
                "counterpart": "다낭",
                "counterpartCode": "DAD",
                "international": True,
                "scheduledTime": "06:05",
                "estimatedTime": "06:19",
                "status": "도착",
                "gate": "5",
            },
        )

    def test_departure_counterpart_and_unchanged_time(self):
        dep = flights.parse_flight_status(STATUS_XML)[0][1]
        self.assertEqual(dep["direction"], "departure")
        self.assertEqual(dep["counterpart"], "제주")
        self.assertFalse(dep["international"])
        self.assertIsNone(dep["estimatedTime"])  # 예정 = 변경이면 표시하지 않음
        self.assertIsNone(dep["gate"])

    def test_sort_and_dedup(self):
        items, _ = flights.parse_flight_status(STATUS_XML)
        departures = [f for f in flights.sort_flights(items) if f["direction"] == "departure"]
        self.assertEqual([f["flightNo"] for f in departures], ["BX8101", "7C102"])
        self.assertIsNone(departures[0]["status"])

    def test_portal_error(self):
        with self.assertRaisesRegex(ValueError, "SERVICE_KEY_IS_NOT_REGISTERED_ERROR"):
            flights.parse_flight_status(PORTAL_ERROR_XML)

    def test_result_code_error(self):
        with self.assertRaises(ValueError):
            flights.parse_flight_status("<response><header><resultCode>99</resultCode></header></response>")


class ParseTagoScheduleTest(unittest.TestCase):
    def test_sorted_and_mapped(self):
        schedule = flights.parse_tago_schedule(tago_json({"item": TAGO_ITEMS}))
        self.assertEqual([f["flightNo"] for f in schedule], ["OZ8141", "KE1903"])
        self.assertEqual(
            schedule[0],
            {
                "flightNo": "OZ8141",
                "airline": "아시아나항공",
                "departureTime": "08:20",
                "arrivalTime": "09:05",
                "economyFare": 57900,
                "businessFare": None,  # 0원 = 좌석 없음
            },
        )

    def test_single_item_object(self):
        self.assertEqual(len(flights.parse_tago_schedule(tago_json({"item": TAGO_ITEMS[0]}))), 1)

    def test_empty_items(self):
        self.assertEqual(flights.parse_tago_schedule(tago_json("")), [])

    def test_portal_error_xml(self):
        with self.assertRaisesRegex(ValueError, "30"):
            flights.parse_tago_schedule(PORTAL_ERROR_XML)

    def test_result_code_error(self):
        text = json.dumps({"response": {"header": {"resultCode": "99", "resultMsg": "INVALID_REQUEST_PARAMETER_ERROR"}}})
        with self.assertRaises(ValueError):
            flights.parse_tago_schedule(text)


if __name__ == "__main__":
    unittest.main()
