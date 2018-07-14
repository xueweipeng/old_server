# -*- coding:utf-8 -*-
import unittest
from app.location import GeoInfo


class TestLocation(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_location(self):
        ret = GeoInfo.get_geo_from_name('北京')
        print ret


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestLocation("test_location"))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
