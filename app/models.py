# -*- coding:utf-8 -*-

from datetime import datetime
# import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask import current_app, request
from . import db
import time


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # 登录名唯一索引 根据设计要求，用户名加密码登录。如果系统改用email登录，则username存放email即可。
    username = db.Column(db.String(64), unique=True, index=True)
    # 用户真实姓名
    realname = db.Column(db.String(64))
    # 邮件和手机用于用于找回密码
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    # 模型中不使用外键约束，程序保证约束一致性
    role_id = db.Column(db.Integer, nullable=False)
    # 验证用户，保留字段
    # confirmed = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    # 删除last_login_time，专门使用login_log表来记录登录历史。
    # last_login_time = db.Column(db.DateTime())
    creator_id = db.Column(db.Integer)
    updator_id = db.Column(db.Integer)
    update_time = db.Column(db.DateTime(), default=datetime.now)
    enable = db.Column(db.Boolean, default=True)

    @staticmethod
    def insert_master():
        users = [
            ('admininstrator', '管理员', 'aaaa', 'admin@test-gov.com', '13099999999', 1),
            ('tester', '测试用户', '123', 'tester@test-gov.com', '13087654321', 2),
        ]
        # 仅当表为空时插入元数据
        if User.query.count() == 0:
            for user_info in users:
                user = User(username=user_info[0])
                user.realname = user_info[1]
                user.password = user_info[2]
                user.email = user_info[3]
                user.phone = user_info[4]
                user.role_id = user_info[5]
                db.session.add(user)
            db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %r>' % self.username

    # 下面两个函数允许设置password，就像User包括password属性一样。但不能读取password.
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_administrator(self):
        return self.role_id == 1

    def generate_auth_token(self, expiration=3600 * 24):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        stamp = int(time.mktime(self.update_time.timetuple()))
        return s.dumps(dict(id=self.id, stamp=stamp))

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # token 过期
        except BadSignature:
            return None
        user = User.query.get(data.get('id', 0))
        stamp = data.get('stamp', None)
        # 用户不存在
        if user is None or stamp is None:
            return None
        # 用户被禁用
        if not user.enable:
            return None
        # 用户的密码已修改或禁用
        stamp_now = int(time.mktime(user.update_time.timetuple()))
        if stamp != stamp_now:
            return None
        return user


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    enable = db.Column(db.Boolean, default=True)

    @staticmethod
    def insert_master():
        # 系统管理员的id为1，普通用户的id为2
        roles = [
            '系统管理员',
            '普通用户',
            '城市管理员'
        ]
        # 仅当表为空时插入元数据
        if Role.query.count() == 0:
            for role_name in roles:
                role = Role(name=role_name)
                db.session.add(role)
            db.session.commit()

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)

    def __repr__(self):
        return '<Role %r>' % self.name


class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    enable = db.Column(db.Boolean, default=True)
    @staticmethod
    def insert_master():
        menus = [
            '基本数据',
            '车辆查询',
            '地图概览'
        ]
        # 仅当表为空时插入元数据
        if Menu.query.count() == 0:
            for menu_name in menus:
                menu = Menu(name=menu_name)
                db.session.add(menu)
            db.session.commit()

    @staticmethod
    def get_all_menus():
        menus = Menu.query.all()
        result = []
        for menu in menus:
            # result.append(dict(id=menu.id, name=menu.name))
            result.append(menu.name)
        return result

    def __repr__(self):
        return '<Menu %r>' % self.name


class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    center = db.Column(db.String(32))
    create_time = db.Column(db.DateTime(), default=datetime.now)
    enable = db.Column(db.Boolean, default=False)

    @staticmethod
    def insert_master():
        cities = [
            '北京',
            '上海',
            '南京'
        ]
        # 仅当表为空时插入元数据
        if City.query.count() == 0:
            for city_name in cities:
                city = City(name=city_name)
                city.enable = True
                db.session.add(city)
            db.session.commit()

    @staticmethod
    def get_all_cities():
        cities = City.query.all()
        result = []
        for city in cities:
            result.append(dict(id=city.id, name=city.name))
        return result

    def __repr__(self):
        return '<City %r>' % self.name


class R_User_City(db.Model):
    __tablename__ = 'r_user_cities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    city_id = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now)

    @staticmethod
    def insert_master():
        if R_User_City.query.count() == 0:
            r1 = R_User_City(user_id=2, city_id=1)
            r2 = R_User_City(user_id=2, city_id=2)
            db.session.add(r1)
            db.session.add(r2)
            db.session.commit()


class R_Role_Menu(db.Model):
    __tablename__ = 'r_role_menus'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, nullable=False)
    menu_id = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now)

    @staticmethod
    def insert_master():
        if R_Role_Menu.query.count() == 0:
            r1 = R_Role_Menu(role_id=2, menu_id=1)
            db.session.add(r1)
            db.session.commit()

    @staticmethod
    def get_menus(role_id):
        pass


class CityInfo(db.Model):
    __tablename__ = 'city_info'
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(32))
    total_bicycles = db.Column(db.Integer, nullable=False)
    total_reg_users = db.Column(db.Integer, default=0)
    distance_per_order = db.Column(db.Float, default=0)
    duration_per_order = db.Column(db.Float, default=0)
    total_reduce_carbon = db.Column(db.Float, default=0)
    person_per_order = db.Column(db.Float, default=0)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    update_time = db.Column(db.DateTime(), default=datetime.now)

    @staticmethod
    def insert_master():
        cities = [
            (1, 1040000),
            (2, 700000),
            (3, 250000),
        ]
        # 仅当表为空时插入元数据
        if CityInfo.query.count() == 0:
            for city in cities:
                city_info = CityInfo(city_id=city[0], total_bicycles=city[1])
                db.session.add(city_info)
            db.session.commit()


class Grid(db.Model):
    __tablename__ = 'grids'
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(32))
    name = db.Column(db.String(64))
    maintainer = db.Column(db.String(32))
    phone = db.Column(db.String(32))
    bikes_in_grid = db.Column(db.Integer, nullable=False, default=0)
    update_time = db.Column(db.DateTime(), default=datetime.now)


class DefaultMaintainer(db.Model):
    __tablename__ = 'default_maintainer'
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(32), unique=True)
    maintainer = db.Column(db.String(32))
    phone = db.Column(db.String(32))
    update_time = db.Column(db.DateTime(), default=datetime.now)


class GridMaintainer(db.Model):
    __tablename__ = 'grids_maintainer'
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(32))
    grid_name = db.Column(db.String(64))
    maintainer = db.Column(db.String(32))
    phone = db.Column(db.String(32))
    update_time = db.Column(db.DateTime(), default=datetime.now)


class GridDate(db.Model):
    __tablename__ = 'grids_date'
    id = db.Column(db.Integer, primary_key=True)
    update_date = db.Column(db.Date(), nullable=False)
    ht = db.Column(db.String(16))
    city_name = db.Column(db.String(32))
    grid_name = db.Column(db.String(64))
    bikes_in_grid = db.Column(db.Integer, nullable=False, default=0)
    update_time = db.Column(db.DateTime(), default=datetime.now)

class DataV(db.Model):
    __tablename__ = 'datav'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    screen_id = db.Column(db.String(64))
    token = db.Column(db.String(64))
    enable_token = db.Column(db.Boolean)

class LoginLog(db.Model):
    __tablename__ = 'login_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    remote_ip = db.Column(db.String(32))
    proxy_ip = db.Column(db.String(64))
    user_agent = db.Column(db.String(128))
    create_time = db.Column(db.DateTime(), default=datetime.now)

    @staticmethod
    def insert(user):
        # 存在nginx
        proxy_ip = request.headers.get('X-Forwarded-For', 'unknown')
        if proxy_ip != 'unknown':
            # An 'X-Forwarded-For' header includes a comma separated list of the
            # addresses, the first address being the actual remote address.
            remote_ip = proxy_ip.encode('utf-8').split(b',')[0].strip()
        else:
            remote_ip = request.remote_addr or 'unknown'
        user_agent = request.headers.get('User-Agent', 'unknown')
        login_log = LoginLog(user_id=user.id, remote_ip=remote_ip,
                             proxy_ip=proxy_ip, user_agent = user_agent)
        db.session.add(login_log)
        db.session.commit()





