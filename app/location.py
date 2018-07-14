# -*- coding:utf-8 -*-

import urllib2
import json

key = 'E876XszcdcLTY92FYn6hqXCBhduaneUL'


class GeoInfo:
    @staticmethod
    def get_geo_from_name(city_name):
        url = '''http://api.map.baidu.com/geocoder/v2/?address={0}&output=json&ak={1}'''\
           .format(city_name, key)
        req = urllib2.urlopen(url)
        page = req.read()
        json_result = json.loads(page)
        if json_result['status'] == 0:
            d_obj = json_result['result']
            d_location = d_obj['location']
            return str(d_location['lng']) + ',' + str(d_location['lat'])
        else:
            return json_result['status']
