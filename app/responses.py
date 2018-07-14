# -*- coding:utf-8 -*-

from flask import jsonify


class JsonResult:
    def __init__(self, code=200, msg='success', data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def setError(self, code, msg):
        self.code = code
        self.msg = msg

    def setData(self, data):
        self.data = data

    def to_json(self):
        return jsonify(dict(code=self.code, msg=self.msg, data=self.data))


def response_401():
    return JsonResult(401, msg='用户认证失败或过期，请重新登录', data=None).to_json()


def response_404():
    return JsonResult(404, msg='请求的资源不存在', data=None).to_json()