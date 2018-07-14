# -*- coding:utf-8 -*-
from . import grid
from .. import mysql_conn
from ..responses import JsonResult
from ..models import City, DefaultMaintainer, GridMaintainer
from ..utils_ads import get_real_table
from ..decorators import login_required, city_auth_required
from ..bike_calculator import bikenum_calculator, calculator_area, calculator_rail, calculator_area_counts, \
    calculator_city_counts, city_district,district_path_find,district_center_find, limit_quantity
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@grid.route('/info/<int:city_id>', methods=['POST', 'GET'])
@login_required
@city_auth_required
def get_grid_info(city_id):
    return None


@grid.route('/grid_detail/<int:city_id>/<int:grid_id>', methods=['POST', 'GET'])
@login_required
def get_gird_detail(city_id, grid_id):
    return None


def get_path_center(path_list):
    lng_list = []
    lat_list = []
    for c in path_list:
        li = c.split(',')
        lng_list.append(float(li[0]))
        lat_list.append(float(li[1]))

    lng_avg = sum(lng_list) / len(lng_list)
    lat_avg = sum(lat_list) / len(lat_list)
    return [str(lng_avg), str(lat_avg)]
