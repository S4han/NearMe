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
<item><dirTp>null</dirTp><govNm>405</govNm><localX>126.515656</localX><localY>33.499888</localY><mobiNum>0</mobiNum><stationId>405001743</stationId><stationNm>제주버스터미널(가상정류소)</stationNm><upd>2026-07-28 09:28:44</upd><useYn>Y</useYn></item>
<item><dirTp>null</dirTp><govNm>405</govNm><localX>126.516515</localX><localY>33.498389</localY><mobiNum>0</mobiNum><stationId>405002353</stationId><stationNm>차고지(가상)</stationNm><upd>2026-07-28 09:28:44</upd><useYn>Y</useYn></item>
<item><dirTp>null</dirTp><govNm>405</govNm><localX>126.5197</localX><localY>33.501633</localY><mobiNum>0</mobiNum><stationId>405000157</stationId><stationNm>중앙마을</stationNm><upd>2026-07-28 09:28:44</upd><useYn>Y</useYn></item>
</items></body></response>"""

ARRIVALS_JSON = """[{"ARRV_STATION_ID":405000153,"ROUTE_SUB_NM":"제주버스터미널(종점)","VH_ID":7983662,"ROUTE_ID":405246201,"ROUTE_NUM":"462","PLATE_NO":"제주79아3662","CURR_STATION_ID":405000601,"PREDICT_TRAV_TM":23,"REMAIN_STATION":16,"CURR_STATION_NM":"광평동로","LOW_PLATE_TP":"Y"},
{"ARRV_STATION_ID":405000153,"ROUTE_SUB_NM":"제주버스터미널(종점)","VH_ID":7983663,"ROUTE_ID":405246101,"ROUTE_NUM":"461","PLATE_NO":"제주79아3663","CURR_STATION_ID":405000372,"PREDICT_TRAV_TM":19,"REMAIN_STATION":12,"CURR_STATION_NM":"남녕고등학교","LOW_PLATE_TP":"Y"},
{"ARRV_STATION_ID":405000153,"ROUTE_SUB_NM":"제주버스터미널","VH_ID":7983133,"ROUTE_ID":405320234,"ROUTE_NUM":"202","PLATE_NO":"제주79아3133","CURR_STATION_ID":406000710,"PREDICT_TRAV_TM":114,"REMAIN_STATION":106,"CURR_STATION_NM":"하모3리","LOW_PLATE_TP":"N"}]"""

ROUTES_JSON = """[{"STATION_NM":"제주버스터미널","ROUTE_SUB_NM":"성산항(종점)","ORGT_NM":"제주국제공항1(표선,성산,남원)","ROUTE_ID":405411101,"ROUTE_NUM":"111","DST_STATION_ID":406002128,"DST_NM":"성산항(종점)","ROUTE_NM":"111-1","STATION_ID":405000153,"ORGT_STATION_ID":405001897},
{"STATION_NM":"제주버스터미널","ROUTE_SUB_NM":"남원환승정류장(남원읍사무소)","ORGT_NM":"제주국제공항2(일주동로, 516도로)","ROUTE_ID":405410111,"ROUTE_NUM":"101","DST_STATION_ID":406001604,"DST_NM":"남원환승정류장(남원읍사무소)","ROUTE_NM":"101-11","STATION_ID":405000153,"ORGT_STATION_ID":405002101},
{"STATION_NM":"제주버스터미널","ROUTE_SUB_NM":"남원환승정류장(남원읍사무소)","ORGT_NM":"제주국제공항2(일주동로, 516도로)","ROUTE_ID":405410111,"ROUTE_NUM":"101","DST_STATION_ID":406001604,"DST_NM":"남원환승정류장(남원읍사무소)","ROUTE_NM":"101-11","STATION_ID":405000153,"ORGT_STATION_ID":405002101}]"""


# JTBIS Bus(노선 목록): 실제 응답 형식 + 테스트용 노선(405104309, 405246101) 추가
BUS_XML = """<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items>
<item><dstStationId>406001556</dstStationId><govNm>null</govNm><orgtStationId>406000976</orgtStationId><routeColor>1</routeColor><routeId>405000001</routeId><routeLen>9951</routeLen><routeNm>5000-1</routeNm><routeNum>5000</routeNum><routeSubNm>대정오일시장</routeSubNm><routeTp>43</routeTp><stationCnt>13</stationCnt><upd>2017-08-29 21:18:42</upd><useYn>N</useYn></item>
<item><routeId>405104309</routeId><routeNm>43-1</routeNm><routeNum>43-1</routeNum><routeSubNm>제주버스터미널(종점)</routeSubNm><useYn>Y</useYn></item>
<item><routeId>405246101</routeId><routeNm>461-1</routeNm><routeNum>461</routeNum><routeSubNm>제주버스터미널(종점)</routeSubNm><useYn>Y</useYn></item>
</items></body></response>"""

# JTBIS BusArrives: 실제 응답(운행 안 하는 노선 arrvVhId=0 포함) + 같은 차량 중복 항목
BUS_ARRIVES_XML = """<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items>
<item><arrvVhId>0</arrvVhId><calcDate>2025-05-08T17:44:48+09:00</calcDate><leftStation>0</leftStation><predictTravTm>0</predictTravTm><routeId>405104301</routeId><stationOrd>49</stationOrd><updnDir>0</updnDir></item>
<item><arrvVhId>7983545</arrvVhId><calcDate>2025-05-08T17:44:48+09:00</calcDate><leftStation>17</leftStation><predictTravTm>42</predictTravTm><routeId>405104309</routeId><stationOrd>47</stationOrd><updnDir>0</updnDir></item>
<item><arrvVhId>7983545</arrvVhId><calcDate>2025-05-08T17:44:48+09:00</calcDate><leftStation>17</leftStation><predictTravTm>42</predictTravTm><routeId>405104309</routeId><stationOrd>48</stationOrd><updnDir>0</updnDir></item>
<item><arrvVhId>7983663</arrvVhId><calcDate>2025-05-08T17:44:48+09:00</calcDate><leftStation>12</leftStation><predictTravTm>19</predictTravTm><routeId>405246101</routeId><stationOrd>30</stationOrd><updnDir>0</updnDir></item>
</items></body></response>"""

# JTBIS StationRoutePs: 실제 응답(2017년 폐지 경유 useYn=N) + 사용 중 경유
STATION_ROUTE_PS_XML = """<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items>
<item><routeDist>17913</routeDist><routeId>405005002</routeId><stationId>405000153</stationId><stationOrd>44</stationOrd><upd>2017-08-25 01:23:39</upd><updnDir>0</updnDir><useYn>N</useYn><waypointOrd>107</waypointOrd></item>
<item><routeDist>3000</routeDist><routeId>405246101</routeId><stationId>405000153</stationId><stationOrd>30</stationOrd><updnDir>0</updnDir><useYn>Y</useYn></item>
<item><routeDist>4000</routeDist><routeId>405104309</routeId><stationId>405000153</stationId><stationOrd>47</stationOrd><updnDir>0</updnDir><useYn>Y</useYn></item>
<item><routeDist>4100</routeDist><routeId>405104309</routeId><stationId>405000153</stationId><stationOrd>48</stationOrd><updnDir>0</updnDir><useYn>Y</useYn></item>
<item><routeDist>0</routeDist><routeId>405000001</routeId><stationId>405000153</stationId><stationOrd>1</stationOrd><updnDir>0</updnDir><useYn>Y</useYn></item>
</items></body></response>"""


class ParseStationsTest(unittest.TestCase):
    def test_only_in_use_and_real_stations(self):
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


class JtbisFallbackTest(unittest.TestCase):
    def setUp(self):
        self.routes = jeju_bus.parse_bus_routes(BUS_XML)

    def test_bus_routes(self):
        self.assertEqual(len(self.routes), 3)
        self.assertFalse(self.routes["405000001"]["inUse"])
        self.assertEqual(self.routes["405246101"]["routeNum"], "461")

    def test_arrivals_only_real_vehicles_dedup_sorted(self):
        arrivals = jeju_bus.parse_jtbis_arrivals(BUS_ARRIVES_XML, self.routes)
        self.assertEqual([(a["routeNum"], a["minutes"]) for a in arrivals], [("461", 19), ("43-1", 42)])
        self.assertEqual(arrivals[1]["remainStations"], 17)
        self.assertEqual(arrivals[1]["destination"], "제주버스터미널(종점)")
        self.assertIsNone(arrivals[0]["currentStationName"])

    def test_arrivals_unknown_route_falls_back_to_id(self):
        arrivals = jeju_bus.parse_jtbis_arrivals(BUS_ARRIVES_XML, {})
        self.assertEqual(arrivals[0]["routeNum"], "405246101")

    def test_station_routes_in_use_only(self):
        routes = jeju_bus.parse_jtbis_station_routes(STATION_ROUTE_PS_XML, self.routes)
        self.assertEqual([r["routeNum"] for r in routes], ["43-1", "461"])


if __name__ == "__main__":
    unittest.main()
