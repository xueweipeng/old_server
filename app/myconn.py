# -*- coding: utf-8 -*-

from __future__ import with_statement

import os
import threading
import time
from copy import copy
from UserList import UserList

import _mysql
import MySQLdb

from logger import Logger

try:
    from threading import current_thread
except:
    from threading import currentThread

    def current_thread():
        t = currentThread()
        t.ident = id(t)
        return t


logger = Logger("sql_query_log.log").getLogger()


def escape(var):
    '''这里假定连接数据库都是使用utf8的。'''
    if var is None:
        return ''
    if isinstance(var, unicode):
        var = var.encode('utf8')
    if not isinstance(var, str):
        var = str(var)
    return _mysql.escape_string(var)


class _ConnectionPool(threading.Thread):
    __mutex = threading.Lock()
    __svrs = {}
    __svrs_ctx = {}

    def __new__(cls, host, user, passwd, db, port=3306):
        lock = _ConnectionPool.__mutex
        svrs = _ConnectionPool.__svrs

        with lock:
            svr_ident = "%s:%s:%s" % (host, port, db)
            obj = svrs.get(svr_ident)
            if obj is None:
                obj = svrs[svr_ident] = object.__new__(cls)

        return obj

    def __init__(self, host, user, psw, db, port=3306):
        with _ConnectionPool.__mutex:
            svrs_ctx = _ConnectionPool.__svrs_ctx
            svr_ident = "%s:%s:%s" % (host, port, db)

            if not svrs_ctx.get(svr_ident):
                threading.Thread.__init__(
                    self,
                    target=self._guard_conns,
                    name="%s_conn_pool" % svr_ident)
                svrs_ctx[svr_ident] = self

                self._db = db
                self._host = host
                self._user = user
                self._psw = psw
                self._port = int(port)

                # self._pid = os.getpid()
                self.__conns = {}

                self.setDaemon(True)
                self.start()

    def __del__(self):
        self._disconnect()

    def _disconnect(self):
        pid = os.getpid()
        self.__wrap_conns.pop(pid, None)
        conns = self.__conns.pop(pid, {})
        for conn in conns.itervalues():
            try:
                conn.close()
            except:
                pass

    @property
    def _connections(self):
        pid = os.getpid()
        conns = self.__conns.get(pid)
        if conns is None:
            conns = self.__conns[pid] = {}
        return conns

    def _guard_conns(self):
        while True:
            try:
                keepings = set(ident for ident in self._connections.keys())
                actives = set(thd.ident for thd in threading.enumerate()
                              if thd.isAlive())

                useless = keepings - actives
                map(lambda ident: self._release_connection(ident), useless)

            except Exception, e:
                print "conn_pool error (_threadChecker) : %s" % str(e)

            finally:
                time.sleep(5 * 60)

    def _new_connection(self):
        conn = MySQLdb.Connect(
            db=self._db,
            host=self._host,
            user=self._user,
            passwd=self._psw,
            port=self._port,
            local_infile=True,
            charset='utf8')

        return conn

    def _release_connection(self, ident):
        try:
            conn = self._connections.pop(ident, None)
            conn and conn.close()
        except Exception, e:
            print 'sqlpool error (_releaseConnection) : %s' % str(e)

    def _reconnect(self, ident):
        self._release_connection(ident)
        conn = self._new_connection()
        self._connections[ident] = conn
        return conn

    def get_connection(self):
        ident = current_thread().ident
        try:
            return self._connections.get(ident) or self._reconnect(ident)
        except:
            return self._reconnect(ident)


class DataRow(object):
    """Wrapper for db result(tuple). Support for d[index] or d['column'] access

    Read only object.
    """

    def __init__(self, rs, column_map):
        """
        rs: db result, which are cursor return.
        column_map: {column_name: index, ...}
        """
        self._data = list(rs)
        self._column_map = column_map

        self.iterkeys = self.keys = self.columns
        self.itervalues = self.values
        self.iteritems = self.items
        self.has_key = self.has_column

    def __repr__(self):
        kvs = self._column_map.items()
        kvs.sort(cmp=lambda a, b: cmp(a[1], b[1]))
        ks = [kv[0] for kv in kvs]
        return str(dict(zip(ks, self._data)))

    def __getitem__(self, key):
        if not isinstance(key, (int, long)):
            key = self._column_map[key]
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __setitem__(self, key, item):
        i = self._column_map.get(key)
        if i is None:
            self._data.append(item)
            self._column_map[key] = len(self._data) - 1
        else:
            self._data[i] = item

    def __delitem__(self, key):
        raise NotImplementedError()

    def __iter__(self):
        for i in self._data:
            yield i

    def __contains__(self, key):
        return key in self._column_map

    def __str__(self):
        return str(self.to_dict())

    def columns(self):
        return self._column_map.keys()

    def values(self):
        return self._data

    def items(self):
        for k, i in self._column_map.iteritems():
            yield k, self._data[i]

    def has_column(self, column):
        # return self._column_map.has_key(column)
        return column in self._column_map

    def update(self, dict=None, **kwargs):
        for k, v in dict.items():
            self.__setitem__(k, v)

    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]

    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        raise NotImplementedError()

    def popitem(self):
        raise NotImplementedError()

    def to_dict(self):
        """return a dict"""
        d = {}
        for k, v in self.items():
            d[k] = v
        return d


class DataRowCollection(UserList):
    def __init__(self, rows, column_map):
        UserList.__init__(self, None)
        self._column_map = column_map
        self.data = [DataRow(r, copy(self._column_map)) for r in rows]

    def __iter__(self):
        for r in self.data:
            yield r

    def to_list(self):
        """return a list, and DataRow will be a dict"""
        return [r.to_dict() for r in self]


class Cursor:
    @staticmethod
    def new(host, db, user, passwd, port=3306, autocommit=True):
        # connection = MySQLdb.Connect(host=host, db=db, user=user, passwd=passwd,
        #                             port=port, charset='utf8')
        pool = _ConnectionPool(host, user, passwd, db, port)
        connection = pool.get_connection()

        connection.ping(True)
        c = Cursor(connection, autocommit)
        return c

    def __init__(self, connection, autocommit):
        self.connection = connection
        self.cursor = connection.cursor()
        self.dict_cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        self.autocommit(autocommit)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.close()

    def autocommit(self, autocommit):
        self.cursor.connection.autocommit(autocommit)

    def close(self):
        try:
            self.cursor and self.cursor.close()
            self.dict_cursor and self.dict_cursor.close()
        except:
            pass
        finally:
            self.cursor = None
            self.dict_cursor = None

    def execute(self, sql, params=None):
        formated_params = self._format_params(params)
        t0 = time.time()
        if formated_params:
            result = self.cursor.execute(sql, formated_params)
        else:
            result = self.cursor.execute(sql)
        if time.time() - t0 > 1:
            logger.error(
                "cast_time:{0}\tsql:{1}".format(time.time() - t0, sql))
        else:
            logger.info("cast_time:{0}\tsql:{1}".format(time.time() - t0, sql))
        return result

    def execute_dict(self, sql, params=None):
        formated_params = self._format_params(params)
        t0 = time.time()
        if formated_params:
            result = self.dict_cursor.execute(sql, formated_params)
        else:
            result = self.dict_cursor.execute(sql)
        if time.time() - t0 > 1:
            logger.error(
                "cast_time:{0}\tsql:{1}".format(time.time() - t0, sql))
        else:
            logger.info("cast_time:{0}\tsql:{1}".format(time.time() - t0, sql))
        return result

    def fetchone(self, sql, params=None, original=False):
        if original:
            self.execute(sql, params)
            return self.cursor.fetchone()
        else:
            self.execute_dict(sql, params)
            return self.dict_cursor.fetchone()

    def fetchall(self, sql, params=None, original=False):
        if original:
            self.execute(sql, params)
            return self.cursor.fetchall()
        else:
            self.execute_dict(sql, params)
            return self.dict_cursor.fetchall()

    def _format_params(self, params):
        if params is None:
            return []
        flag = isinstance(params, list) or isinstance(params, tuple)
        return params if flag else [params]
