#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/10/8 8:35
# File    : rebuild_proxy.py
# Version : 1.0
# Describe: 代理池重建
# Update  :
'''

import pymongo
import proxyPool
import configManager
import random

HEADERS = {
    "User-Agent": random.choice(configManager.headers)
}

# 本地 mongodb 参数
username = "localhost"
password = 27017

# 连接 mongodb
client = pymongo.MongoClient(username, password)
# 创建数据库
proxyDB = client['proxyIP_DB']
proxyIP = proxyDB["proxyIP"]

class DataBase_Rebuild(object):
    def delete_all(self):
        print(u"[*] 开始清理代理池")
        try:
            # 清除表内容，不能用drop方法，这样会将整个表删除
            proxyIP.remove({})
            print(u"[+] 清理完成")
        except:
            print(u"[-] 清理失败")

    def proxy_crawl(self):
        proxyPool.CrawlProxyIP(HEADERS).crawl_ip2(HEADERS)

    def disposer(self):
        self.delete_all()
        self.proxy_crawl()

rebuild = DataBase_Rebuild()
rebuild.disposer()
