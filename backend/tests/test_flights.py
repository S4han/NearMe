"""공항·항공편 응답 변환 테스트. 샘플은 한국공항공사 실시간 항공기 운항정보 검색 GW V1(2026-08) 활용가이드 예제 기반.

실행: backend 폴더에서 `python -m unittest discover tests`
"""

import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import KST  # noqa: E402
from services import flights  # noqa: E402

# KAC 이전 API(getFlightStatusList) 예제 형식 — GW도 필드가 같다: 김해 국제선 도착 + 국내선 출발편, 페이지 경계 중복 항목
STATUS_XML = """<?xml version="1.0" encoding="UTF-8"?><response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items>
<item><airFln>LJ074</airFln><airlineEnglish>JINAIR</airlineEnglish><airlineKorean>진에어</airlineKorean><airport>PUS</airport><arrivedEng>GIMHAE</arrivedEng><arrivedKor>부산/김해</arrivedKor><boardingEng>DANANG</boardingEng><boardingKor>다낭</boardingKor><city>DAD</city><etd>0619</etd><gate>5</gate><io>I</io><line>국제</line><rmkEng>ARRIVED </rmkEng><rmkKor>도착</rmkKor><std>0605</std></item>
<item><airFln>7C102</airFln><airlineEnglish>JEJU AIR</airlineEnglish><airlineKorean>제주항공</airlineKorean><airport>PUS</airport><arrivedEng>JEJU</arrivedEng><arrivedKor>제주</arrivedKor><boardingEng>GIMHAE</boardingEng><boardingKor>부산/김해</boardingKor><city>CJU</city><etd>0600</etd><io>O</io><line>국내</line><rmkEng>DEPARTED</rmkEng><rmkKor>출발</rmkKor><std>0600</std></item>
<item><airFln>BX8101</airFln><airlineKorean>에어부산</airlineKorean><arrivedKor>제주</arrivedKor><boardingKor>부산/김해</boardingKor><city>CJU</city><io>O</io><line>국내</line><std>0550</std></item>
<item><airFln>7C102</airFln><airlineKorean>제주항공</airlineKorean><arrivedKor>제주</arrivedKor><io>O</io><line>국내</line><std>0600</std></item>
<item><airFln></airFln><std>0700</std></item>
</items><numOfRows>10</numOfRows><pageNo>1</pageNo><totalCount>105</totalCount></body></response>"""

# KAC GW flight-search/info 가이드 예제 응답(발췌): <script/>, 빈 <gate/> 포함
GW_XML = """<response> <script/> <header> <resultCode>00</resultCode> <resultMsg>NORMAL SERVICE.</resultMsg> </header> <body> <numOfRows>10</numOfRows> <pageNo>1</pageNo> <totalCount>1740</totalCount> <items>
<item> <boardingKor>청주</boardingKor> <boardingEng>CHEONGJU</boardingEng> <arrivedKor>상하이/푸동</arrivedKor> <arrivedEng>PUDONG</arrivedEng> <airlineKorean>이스타항공</airlineKorean> <airlineEnglish>EASTAR JET</airlineEnglish> <airFln>ZE821A</airFln> <std>0005</std> <etd>0016</etd> <io>O</io> <line>국제</line> <gate/> <rmkKor>출발</rmkKor> <rmkEng>DEPARTED</rmkEng> <city>PVG</city> <airport>CJJ</airport> </item>
<item> <boardingKor>서울/김포</boardingKor> <boardingEng>GIMPO</boardingEng> <arrivedKor>제주</arrivedKor> <arrivedEng>JEJU</arrivedEng> <airlineKorean>파라타항공</airlineKorean> <airlineEnglish>PARATA AIR</airlineEnglish> <airFln>WE6501</airFln> <std>0600</std> <etd>0620</etd> <io>O</io> <line>국내</line> <gate>13</gate> <rmkKor>출발</rmkKor> <rmkEng>DEPARTED</rmkEng> <city>CJU</city> <airport>GMP</airport> </item>
<item> <boardingKor>타이페이/타오위안</boardingKor> <boardingEng>TAOYUAN</boardingEng> <arrivedKor>제주</arrivedKor> <arrivedEng>JEJU</arrivedEng> <airlineKorean>이스타항공</airlineKorean> <airlineEnglish>EASTAR JET</airlineEnglish> <airFln>ZE886</airFln> <std>0605</std> <etd>0627</etd> <io>I</io> <line>국제</line> <gate>4</gate> <rmkKor>도착</rmkKor> <rmkEng>ARRIVED </rmkEng> <city>TPE</city> <airport>CJU</airport> </item>
</items> </body> </response>"""

# 2026-10-13 실측 응답(제주 출발 08:00~12:00, schFln 없이 호출) 발췌
REAL_CJU_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header>
<body><numOfRows>5</numOfRows><pageNo>1</pageNo><totalCount>83</totalCount><items>
<item><boardingKor>제주</boardingKor><boardingEng>JEJU</boardingEng><arrivedKor>닝보</arrivedKor><arrivedEng>NINGBO</arrivedEng><airlineKorean>춘추항공</airlineKorean><airlineEnglish>SPRING AIRLINES</airlineEnglish><airFln>9C8626</airFln><std>0800</std><etd>0802</etd><io>O</io><line>국제</line><gate>22</gate><rmkKor>출발</rmkKor><rmkEng>DEPARTED</rmkEng><city>NGB</city><airport>CJU</airport></item>
<item><boardingKor>제주</boardingKor><boardingEng>JEJU</boardingEng><arrivedKor>광주</arrivedKor><arrivedEng>GWANGJU</arrivedEng><airlineKorean>제주항공</airlineKorean><airlineEnglish>JEJU AIR</airlineEnglish><airFln>7C302</airFln><std>0810</std><etd>0828</etd><io>O</io><line>국내</line><gate>1A</gate><rmkKor>출발</rmkKor><rmkEng>DEPARTED</rmkEng><city>KWJ</city><airport>CJU</airport></item>
<item><boardingKor>제주</boardingKor><boardingEng>JEJU</boardingEng><arrivedKor>양양</arrivedKor><arrivedEng>YANGYANG</arrivedEng><airlineKorean>파라타항공</airlineKorean><airlineEnglish>PARATA AIR</airlineEnglish><airFln>WE6702</airFln><std>0800</std><etd>0811</etd><io>O</io><line>국내</line><gate>5</gate><rmkKor>출발</rmkKor><rmkEng>DEPARTED</rmkEng><city>YNY</city><airport>CJU</airport></item>
</items></body></response>"""

# 공공데이터포털 게이트웨이 오류(인증키 미등록) — XML로만 응답
PORTAL_ERROR_XML = """<OpenAPI_ServiceResponse><cmmMsgHeader><errMsg>SERVICE ERROR</errMsg><returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg><returnReasonCode>30</returnReasonCode></cmmMsgHeader></OpenAPI_ServiceResponse>"""


class AirportsTest(unittest.TestCase):
    def test_codes_unique(self):
        codes = [a["code"] for a in flights.AIRPORTS]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(flights.AIRPORTS_BY_CODE["CJU"]["name"], "제주국제공항")

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


def _flight(flight_no, airline, std="09:05", etd="09:23", gate="12", city="WJU", status="출발"):
    return {
        "flightNo": flight_no,
        "airline": airline,
        "direction": "departure",
        "counterpart": "원주",
        "counterpartCode": city,
        "international": False,
        "scheduledTime": std,
        "estimatedTime": etd,
        "status": status,
        "gate": gate,
    }


class MergeCodesharesTest(unittest.TestCase):
    def test_merges_same_aircraft_and_picks_operating_number(self):
        # 2026-10-13 제주 출발 실측: 대한항공 KE5242 = 진에어 LJ472(같은 시각·게이트)
        merged = flights.merge_codeshares(
            [_flight("KE5242", "대한항공"), _flight("LJ472", "진에어"), _flight("BX8106", "에어부산", "09:10", None, "13", "PUS", "지연")]
        )
        self.assertEqual([f["flightNo"] for f in merged], ["LJ472", "BX8106"])
        self.assertEqual(merged[0]["codeshares"], [{"flightNo": "KE5242", "airline": "대한항공"}])
        self.assertEqual(merged[1]["codeshares"], [])

    def test_keeps_separate_when_gate_unknown(self):
        merged = flights.merge_codeshares([_flight("KE1001", "대한항공", gate=None), _flight("OZ8901", "아시아나항공", gate=None)])
        self.assertEqual(len(merged), 2)

    def test_keeps_separate_when_times_differ(self):
        merged = flights.merge_codeshares([_flight("KE5242", "대한항공"), _flight("LJ472", "진에어", etd="09:30")])
        self.assertEqual(len(merged), 2)


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

    def test_gw_example(self):
        items, total = flights.parse_flight_status(GW_XML)
        self.assertEqual(total, 1740)
        self.assertEqual([f["flightNo"] for f in items], ["ZE821A", "WE6501", "ZE886"])
        self.assertIsNone(items[0]["gate"])  # 빈 <gate/>
        self.assertEqual(items[0]["counterpart"], "상하이/푸동")
        self.assertEqual(items[0]["estimatedTime"], "00:16")
        arrival = items[2]
        self.assertEqual((arrival["direction"], arrival["counterpart"], arrival["gate"]), ("arrival", "타이페이/타오위안", "4"))

    def test_real_cju_departures(self):
        items, total = flights.parse_flight_status(REAL_CJU_XML)
        self.assertEqual(total, 83)
        ordered = flights.sort_flights(items)
        self.assertEqual([f["flightNo"] for f in ordered], ["9C8626", "WE6702", "7C302"])
        self.assertEqual(
            ordered[2],
            {
                "flightNo": "7C302",
                "airline": "제주항공",
                "direction": "departure",
                "counterpart": "광주",
                "counterpartCode": "KWJ",
                "international": False,
                "scheduledTime": "08:10",
                "estimatedTime": "08:28",
                "status": "출발",
                "gate": "1A",
            },
        )

    def test_portal_error(self):
        with self.assertRaisesRegex(ValueError, "SERVICE_KEY_IS_NOT_REGISTERED_ERROR"):
            flights.parse_flight_status(PORTAL_ERROR_XML)

    def test_result_code_error(self):
        with self.assertRaises(ValueError):
            flights.parse_flight_status("<response><header><resultCode>99</resultCode></header></response>")


if __name__ == "__main__":
    unittest.main()
