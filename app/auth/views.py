# -*- coding:utf-8 -*-

from flask import request, g
from . import auth
from ..models import User, Role, Menu, City, R_Role_Menu, R_User_City, LoginLog
from ..responses import JsonResult, response_404
from ..decorators import login_required


# 在蓝图中使用针对程序全局请求的钩子，必须使用before_app_request修饰器。
@auth.before_app_request
def before_request():
    g.user = None
    token = request.headers.get('X-Token', None)
    if token is not None:
        g.user = User.verify_auth_token(token)


@auth.app_errorhandler(404)
def page_not_found(e):
    return response_404()



# 暂时接受GET与POST双重登录
@auth.route('/login', methods=['GET', 'POST'])
def login():
    return None


@auth.route('/logout')
@login_required
def logout():
    return JsonResult().to_json()