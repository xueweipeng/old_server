# -*- coding:utf-8 -*-
'''
    公共函数
'''
from werkzeug.security import generate_password_hash, check_password_hash


def is_valid(data):
    return True


if __name__ == '__main__':
    passwords = [
        '4Ff7cRd6',
         ]
    for password in passwords:
        print password, generate_password_hash(password)

