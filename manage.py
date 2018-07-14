#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from config import Config

from flask_script import Manager, Shell

from app import create_app, db
from app.models import User, Role, Menu, City, R_User_City, R_Role_Menu, CityInfo
from flask_cors import CORS


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
CORS(app, allow_headers=['X-Token', 'Content-Type'])


# def make_shell_context():
#     return dict(app=app, db=db, User=User, Role=Role)

# manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def createdb():
    db.create_all()
    Role.insert_master()
    User.insert_master()
    Menu.insert_master()
    City.insert_master()
    R_User_City.insert_master()
    R_Role_Menu.insert_master()
    CityInfo.insert_master()


@manager.command
def env():
    print(os.getenv('FLASK_CONFIG'))


if __name__ == '__main__':
    # print(app.url_map)
    manager.run()
