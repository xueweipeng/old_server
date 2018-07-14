# -*- coding:utf-8 -*-
'''
    ads公共函数
'''
from . import mysql_conn


def get_real_table():
    sql = """select position_tab, dt, mt from position_record"""
    result = mysql_conn.fetchone(sql)
    if result is not None:
        position_table = result['position_tab']
        dt = result['dt']
        mt = result['mt']
        return position_table, dt, mt
    return None

