#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:01
# File    : authentication.py
# Version : 1.1
# Describe: 验证模块
# Update  :
        1.新增了retry库，可多次尝试网站连通性，直到连接超时。
'''

import urllib2
import requests
import socket
import spiderData
import pymongo
import gc
from retry import retry

class Authentication(object):
    def __init__(self, headers):
        print("[*] 初始化验证模块")
        self.headers = headers

    def dataBaseVerify(self, dbParams):
        '''
        验证数据库连接状态
        :param dbParams: 数据库连接参数
        :return: 验证通过返回 True，否则返回 False
        '''
        print("[+] 正在验证 MongoDB 数据库连接状态")
        try:
            userName = dbParams["userName"]
            port = dbParams["port"]
            pymongo.MongoClient(userName, port)
            print("[+] 数据库验证通过")
            return True
        except Exception, e:
            print("[+] 数据库验证失败")
            print("ERROR: " + str(e.message))
            return False

    @retry(tries=5, delay=2)
    def httpCodeVerify(self, url):
        '''
        验证 HTTP 状态码
        :return: 验证通过返回 True，否则返回 False
        '''
        print("[+] 正在验证 HTTP 状态码：{0}".format(url))
        try:
            request = urllib2.Request(url, headers=self.headers)
            urllib2.urlopen(request)
            print("[+] HTTP 验证通过：{0}".format(url))
            return True
        except urllib2.HTTPError, e:
            print("[+] HTTP 验证失败：{0}".format(url))
            print("ERROR: " + str(e.code) + " " + spiderData.httpStatusCode[str(e.code)])
            return False

    def proxyVerify(self, url, protocol, ip, port):
        '''
        检查代理IP是否可用
        :param ip:代理IP
        :param port:代理端口
        :param protocol:代理协议
        :return:返回检查结果
        '''
        check_url = url
        proxy_url = "{0}://{1}:{2}".format(protocol, ip, port)
        print("[+] 正在验证代理 IP 可用性")
        socket_timeout = 30
        socket.setdefaulttimeout(socket_timeout)
        try:
            proxy_dict = {
                protocol: proxy_url
            }
            response = requests.get(check_url, proxies=proxy_dict, headers=self.headers)
            code = response.status_code
            print(str(code))
            if code >= 200 and code < 300:
                print("[+] 可用的代理IP和端口： {0}:{1}:{2}".format(protocol, ip, port))
                print("[+] 验证通过")
                return True
            else:
                print("[-] 不可用的代理IP和端口： {0}:{1}:{2}".format(protocol, ip, port))
                return False
        except Exception, e:
            print("[-] 不可用的代理IP和端口： {0}:{1}:{2}".format(protocol, ip, port))
            print("ERROR: " + str(e.message))
            return False
        finally:
            gc.collect()
