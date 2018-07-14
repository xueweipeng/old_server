# -*- coding:utf-8 -*-

import os
import sys
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress
from myconn import Cursor

from config import config

mail = Mail()
db = SQLAlchemy()
compress = Compress()

# TODO: 添加到配置文件中
TEST_GOV_DBHOST = 'xxx.com'
TEST_GOV_DB = 'xxx'
TEST_GOV_DBPORT = 10048
TEST_GOV_DBUSER = 'user'
TEST_GOV_DBPWD = 'password'
mysql_conn = Cursor.new(TEST_GOV_DBHOST, TEST_GOV_DB, TEST_GOV_DBUSER, TEST_GOV_DBPWD, TEST_GOV_DBPORT)

mysql_master_conn = Cursor.new(
    'address.com',
    'master',
    'admin',
    'pwd',
    3306)


reload(sys)
sys.setdefaultencoding('utf-8')


def register_blueprint(app):
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/main')
    from .grid import grid as grid_blueprint
    app.register_blueprint(grid_blueprint, url_prefix='/grid')
    from .maps import maps as maps_blueprint
    app.register_blueprint(maps_blueprint, url_prefix='/maps')


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        # 日志文件的大小限制在 1 M，保留最后 10 个日志文件作为备份
        file_handler = RotatingFileHandler(os.environ.get('FEIDIAN_LOG_PATH') or app.config['FEIDIAN_LOG_PATH'], 'a', 1 * 1024 * 1024, 10)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    compress.init_app(app)

    # Configure SSL if platform supports it
    # if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
    #     from flask.ext.sslify import SSLify
    #     SSLify(app)

    # Create app blueprints
    register_blueprint(app)

    return app

