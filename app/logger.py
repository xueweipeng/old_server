#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: lemon

#coding=utf8

import os
import sys
import logging
from watched_rotating_log import WatchedRotatingFileHandler


class Logger:

    def __init__(self, name, size = 10, backupCount = 50, cacheRecords = 5, print_to_console=True):
        '''
        size : 单个日志文件的大小，单位是M。
        backupCount :备份的最大日志文件数'
        cacheRecords :日志缓存数。达到该数字才会写硬盘。flushLevel以上级别的除外
        '''
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        #logdir = os.path.join(config.PATH.LOG, name)
        logfile = name
        hdlr = WatchedRotatingFileHandler(logfile, 'a', maxBytes=1024*1024 *size, backupCount=backupCount)
        hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        self.logger.addHandler(hdlr)
        if print_to_console:
            #将大于或等于DEBUG级别的信息输出到控件台
            hdlr = logging.StreamHandler(sys.stdout)
            hdlr.setFormatter(logging.Formatter('%(message)s', ''))
            hdlr.setLevel(logging.DEBUG)
            self.logger.addHandler(hdlr)

    def getLogger(self):
        return self.logger

