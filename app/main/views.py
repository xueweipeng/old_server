# -*- coding:utf-8 -*-

from flask import request, g
from . import main
from ..responses import JsonResult, response_404
from ..models import CityInfo
from .. import mysql_conn, mysql_master_conn
from ..decorators import login_required, city_auth_required
from datetime import datetime


@main.route('/company')
@login_required
def get_company_info():
    data = dict(
        company='aaa',  # 企业标识
        name='有限公司',  # 企业名称
    )

    return JsonResult(data=data).to_json()


# 基本数据
@main.route('/info-cities/<int:city_id>')
@login_required
@city_auth_required
def get_city_info(city_id):
   return None


@main.route('/info-city-grids/<int:city_id>')
@login_required
def get_grid_info(city_id):
    return response_404()



@main.route('/points/', methods=['POST'])
@login_required
def get_points_info():
    return None




@main.route('/shanghai')
def get_shanghai():
    return None
