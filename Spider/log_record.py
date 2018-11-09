#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/10/8 11:41
# File    : log_record.py
# Version : 1.0
# Describe: 日志监控模块
# Update  :
'''

import pymongo

# 本地 mongodb 参数
username = "localhost"
port = 27017

# 连接 mongodb
client = pymongo.MongoClient(username, port)
# 创建数据库
logDB = client['Log_DB']
# 创建数据表，用于存储日志信息
logTable = logDB['log_execute']

def log_recorder(current_time, execute_result):
    log_data = {
        "执行时间": current_time,
        "执行结果": execute_result
    }
    logTable.insert_one(log_data)
