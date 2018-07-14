# -*- coding:utf-8 -*-
'''
    修饰器
'''

from functools import wraps

from flask import g, current_app
from responses import JsonResult, response_401
from .models import R_User_City


def login_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        # 可通过配置禁用
        if current_app.config['LOGIN_DISABLED']:
            return func(*args, **kwargs)
        if g.user is None:
            return response_401()
        return func(*args, **kwargs)
    return decorated


# 注意：使用前请保证路由参数中有city_id
def city_auth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        # 如果不校验登录，则不校验城市权限
        if current_app.config['LOGIN_DISABLED']:
            return func(*args, **kwargs)

        city_id = kwargs.get('city_id', 0)
        if g.user is not None and not g.user.is_administrator():
            city_auth = R_User_City.query.filter_by(user_id=g.user.id, city_id=city_id).first()
            if city_auth is None:
                return response_401()
        return func(*args, **kwargs)
    return decorated
