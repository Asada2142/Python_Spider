#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:05
# File    : spiderLog.py
# Version : 1.0
# Describe: 爬虫日志
# Update  :
'''

import logging

LOG_PATH = "SpiderLog.txt"
handler = logging.FileHandler(LOG_PATH)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.INFO)

class SpiderLog(object):
    def __init__(self, log_location):
        self.logger = logging.getLogger(log_location)  # __name__
        self.logger.setLevel(level=logging.INFO)
        self.logger.addHandler(handler)
        self.logger.addHandler(console)

    def info(self, message_info):
        self.logger.info(message_info)

    def warning(self, message_warn):
        self.logger.warn(message_warn)

    def error(self, message_error):
        self.logger.error(message_error)

    def debug(self, message_debug):
        self.logger.debug(message_debug)

    def exception(self, message_exception):
        self.logger.exception(message_exception)
