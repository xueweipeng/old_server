# -*- coding:utf-8 -*-

'''
    程序的配置文件：为flask及扩展提供配置。
'''

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # crsf
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'xxxxxxxxxxx'

    # SqlAlchemy
    # TODO 在当前BI系统中设置为true
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    LOGIN_DISABLED = False  # @login_required都失效，为了自测接口，可设置为True
    db_server_info = {
        'host': '127.0.0.1',
        'port': '3306',
        'schema': 'master',
        'user': 'admin',
        'password': 'xxxxxxxxxxxx'
    }
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}:{port}/{schema}?charset=utf8'.format(
        host=db_server_info['host'],
        port=db_server_info['port'],
        schema=db_server_info['schema'],
        user=db_server_info['user'],
        password=db_server_info['password']
    )

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    LOGIN_DISABLED = False  # @login_required都有效
    FEIDIAN_LOG_PATH = '/data/apps/logs/test_product.log'
    db_server_info = {
        'host': '127.0.0.1',
        'port': '3306',
        'schema': 'master',
        'user': 'admin',
        'password': 'xxxxxxxxxx'
    }
    SQLALCHEMY_DATABASE_URI = 'mysql://{user}:{password}@{host}:{port}/{schema}?charset=utf8'.format(
        host=db_server_info['host'],
        port=db_server_info['port'],
        schema=db_server_info['schema'],
        user=db_server_info['user'],
        password=db_server_info['password']
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


# 增加线上服务器调试配置，利于线上服务器启动时错误的调试，以及线上问题的调试。
class ProductionDebugConfig(ProductionConfig):
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'production_debug': ProductionDebugConfig,

    'default': DevelopmentConfig
}
