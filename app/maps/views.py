# -*- coding:utf-8 -*-

from ..decorators import login_required, city_auth_required
from . import maps
from ..responses import JsonResult
from ..models import CityInfo, R_User_City, City
import Geohash
from .. import mysql_conn, mysql_master_conn
from ..utils_ads import get_real_table
from flask import request


@maps.route('/heatmap/<int:city_id>', methods=['GET', 'POST'])
@login_required
@city_auth_required
def get_city_heatmap(city_id):
    return None
