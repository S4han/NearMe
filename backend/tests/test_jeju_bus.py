"""제주 버스 응답 변환 테스트. 샘플은 2026-10-12 실제 API 응답에서 발췌.

실행: backend 폴더에서 `python -m unittest discover tests`
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services import jeju_bus  # noqa: E402

STATION_XML = """<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items>
<item><dirTp>N</dirTp><govNm>405</govNm><localX>126.521348</localX><localY>33.499916</localY><mobiNum>0</mobiNum><stationId>405000151</stationId><stationNm>용천마을</stationNm><upd>2026-07-28 09:28:44</upd><useYn>N</useYn></item>
<item><dirTp>S</dirTp><govNm>405</govNm><localX>126.514</localX><localY>33.499974</localY><mobiNum>0</mobiNum><stationId>405000153</stationId><stationNm>제주버스터미널</stationNm><upd>2026-07-28 09:28:44</upd><useYn>Y</useYn></item>
<item><dirTp>N</dirTp><govNm>405</govNm><localX>126.514018</localX><localY>33.500139</localY><mobiNum>0</mobiNum><stationId>405000154</stationId><stationNm>제주버스터미널</stationNm><upd>2026-07-28 09:28:44</upd><useYn>Y</useYn></item>
<item><dirTp>null</dirTp><govNm>405</govNm><localX>126.5197</localX><localY>33.501633</localY><mobiNum>0</mobiNum><stationId>405000157</stationId><stationNm>중앙마을</stationNm><upd>2026-07-28 09:28:44</upd><useYn>Y</useYn></item>
</items></body></response>"""

ARRIVALS_JSON = """[{"ARRV_STATION_ID":405000153,"ROUTE_SUB_NM":"제주버스터미널(종점)","VH_ID":7983662,"ROUTE_ID":405246201,"ROUTE_NUM":"462","PLATE_NO":"제주79아3662","CURR_STATION_ID":405000601,"PREDICT_TRAV_TM":23,"REMAIN_STATION":16,"CURR_STATION_NM":"광평동로","LOW_PLATE_TP":"Y"},
{"ARRV_STATION_ID":405000153,"ROUTE_SUB_NM":"제주버스터미널(종점)","VH_ID":7983663,"ROUTE_ID":405246101,"ROUTE_NUM":"461","PLATE_NO":"제주79아3663","CURR_STATION_ID":405000372,"PREDICT_TRAV_TM":19,"REMAIN_STATION":12,"CURR_STATION_NM":"남녕고등학교","LOW_PLATE_TP":"Y"},
{"ARRV_STATION_ID":405000153,"ROUTE_SUB_NM":"제주버스터미널","VH_ID":7983133,"ROUTE_ID":405320234,"ROUTE_NUM":"202","PLATE_NO":"제주79아3133","CURR_STATION_ID":406000710,"PREDICT_TRAV_TM":114,"REMAIN_STATION":106,"CURR_STATION_NM":"하모3리","LOW_PLATE_TP":"N"}]"""

ROUTES_JSON = """[{"STATION_NM":"제주버스터미널","ROUTE_SUB_NM":"성산항(종점)","ORGT_NM":"제주국제공항1(표선,성산,남원)","ROUTE_ID":405411101,"ROUTE_NUM":"111","DST_STATION_ID":406002128,"DST_NM":"성산항(종점)","ROUTE_NM":"111-1","STATION_ID":405000153,"ORGT_STATION_ID":405001897},
{"STATION_NM":"제주버스터미널","ROUTE_SUB_NM":"남원환승정류장(남원읍사무소)","ORGT_NM":"제주국제공항2(일주동로, 516도로)","ROUTE_ID":405410111,"ROUTE_NUM":"101","DST_STATION_ID":406001604,"DST_NM":"남원환승정류장(남원읍사무소)","ROUTE_NM":"101-11","STATION_ID":405000153,"ORGT_STATION_ID":405002101},
{"STATION_NM":"제주버스터미널","ROUTE_SUB_NM":"남원환승정류장(남원읍사무소)","ORGT_NM":"제주국제공항2(일주동로, 516도로)","ROUTE_ID":405410111,"ROUTE_NUM":"101","DST_STATION_ID":406001604,"DST_NM":"남원환승정류장(남원읍사무소)","ROUTE_NM":"101-11","STATION_ID":405000153,"ORGT_STATION_ID":405002101}]"""


class ParseStationsTest(unittest.TestCase):
    def test_only_in_use_stations(self):
        stations = jeju_bus.parse_stations(STATION_XML)
        self.assertEqual([s["id"] for s in stations], ["405000153", "405000154", "405000157"])

    def test_fields(self):
        s = jeju_bus.parse_stations(STATION_XML)[0]
        self.assertEqual(s, {"id": "405000153", "name": "제주버스터미널", "lat": 33.499974, "lng": 126.514, "direction": "S"})

    def test_null_direction(self):
        self.assertIsNone(jeju_bus.parse_stations(STATION_XML)[2]["direction"])

    def test_error_result_code(self):
        with self.assertRaises(ValueError):
            jeju_bus.parse_stations("<response><header><resultCode>99</resultCode></header></response>")


class FindNearbyTest(unittest.TestCase):
    def setUp(self):
        self.stations = jeju_bus.parse_stations(STATION_XML)

    def test_sorted_by_distance_within_radius(self):
        # 제주버스터미널(남쪽 방향) 정류장 바로 옆에서 검색
        found = jeju_bus.find_nearby(self.stations, 33.49997, 126.51401, 300, 10)
        self.assertEqual([s["id"] for s in found], ["405000153", "405000154"])
        self.assertLessEqual(found[0]["distance"], found[1]["distance"])

    def test_limit(self):
        self.assertEqual(len(jeju_bus.find_nearby(self.stations, 33.5, 126.516, 5000, 2)), 2)

    def test_distance(self):
        # 위도 0.001도 ≈ 111m
        self.assertAlmostEqual(jeju_bus.distance_m(33.5, 126.5, 33.501, 126.5), 111, delta=1)


class ParseArrivalsTest(unittest.TestCase):
    def test_sorted_and_mapped(self):
        arrivals = jeju_bus.parse_arrivals(ARRIVALS_JSON)
        self.assertEqual([a["routeNum"] for a in arrivals], ["461", "462", "202"])
        self.assertEqual(
            arrivals[0],
            {
                "routeId": "405246101",
                "routeNum": "461",
                "destination": "제주버스터미널(종점)",
                "minutes": 19,
                "remainStations": 12,
                "currentStationName": "남녕고등학교",
                "plateNo": "제주79아3663",
                "lowFloor": True,
            },
        )
        self.assertFalse(arrivals[2]["lowFloor"])

    def test_empty(self):
        self.assertEqual(jeju_bus.parse_arrivals("[]"), [])
        self.assertEqual(jeju_bus.parse_arrivals(""), [])

    def test_not_a_list(self):
        with self.assertRaises(ValueError):
            jeju_bus.parse_arrivals('{"error": "x"}')


class ParseRoutesTest(unittest.TestCase):
    def test_dedup_and_sorted_by_number(self):
        routes = jeju_bus.parse_routes(ROUTES_JSON)
        self.assertEqual([r["routeName"] for r in routes], ["101-11", "111-1"])
        self.assertEqual(routes[0]["origin"], "제주국제공항2(일주동로, 516도로)")
        self.assertEqual(routes[0]["destination"], "남원환승정류장(남원읍사무소)")


if __name__ == "__main__":
    unittest.main()
