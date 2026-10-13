"""T map 경로 안내 응답 변환 테스트. 샘플은 T map 도보/자동차 경로 안내 응답 형식(GeoJSON) 기반.

실행: backend 폴더에서 `python -m unittest discover tests`
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services import routes  # noqa: E402

PEDESTRIAN_JSON = json.dumps(
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [126.5312, 33.4996]},
                "properties": {"totalDistance": 1234, "totalTime": 925, "index": 0, "pointType": "SP"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": [[126.5312, 33.4996], [126.53, 33.5]]},
                "properties": {"index": 1, "distance": 120, "time": 90},
            },
        ],
    }
)

CAR_JSON = json.dumps(
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [126.5312, 33.4996]},
                "properties": {"totalDistance": 1630, "totalTime": 372, "totalFare": 0, "taxiFare": 4800},
            }
        ],
    }
)


class ParseTmapSummaryTest(unittest.TestCase):
    def test_pedestrian(self):
        self.assertEqual(routes.parse_tmap_summary(PEDESTRIAN_JSON), {"distance": 1234, "seconds": 925})

    def test_car(self):
        self.assertEqual(routes.parse_tmap_summary(CAR_JSON), {"distance": 1630, "seconds": 372})

    def test_error_response(self):
        text = json.dumps({"error": {"id": "400", "category": "tmap", "code": "3102", "message": "서비스 지역이 아닙니다."}})
        with self.assertRaisesRegex(ValueError, "3102"):
            routes.parse_tmap_summary(text)

    def test_missing_totals(self):
        with self.assertRaises(ValueError):
            routes.parse_tmap_summary(json.dumps({"type": "FeatureCollection", "features": []}))


class RequestBodyTest(unittest.TestCase):
    def test_x_is_longitude(self):
        body = routes.request_body(33.4996, 126.5312, 33.51, 126.49)
        self.assertEqual((body["startX"], body["startY"]), ("126.5312", "33.4996"))
        self.assertEqual((body["endX"], body["endY"]), ("126.49", "33.51"))
        self.assertEqual(body["reqCoordType"], "WGS84GEO")
        self.assertEqual(body["startName"], "%EC%B6%9C%EB%B0%9C")  # '출발' URL 인코딩

    def test_round_coord(self):
        self.assertEqual(routes.round_coord(33.499612345), 33.4996)


if __name__ == "__main__":
    unittest.main()
