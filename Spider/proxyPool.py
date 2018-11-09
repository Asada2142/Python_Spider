#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:03
# File    : proxyPool.py
# Version : 1.1
# Describe: 代理池
# Update  :
        1.由于第二个代理网站的页面更改，这里对代理爬取方法做了调整。
'''

import requests
import urllib2
from lxml import etree
from scrapy.selector import Selector
import pymongo
import configManager
import random
import sys
import socket
import time
from multiprocessing import Pool

# 设置默认编码，防止出现中文字符乱码
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

# 本地 mongodb 参数
username = "localhost"
password = 27017

# 连接 mongodb
client = pymongo.MongoClient(username, password)
# 创建数据库
proxyDB = client['proxyIP_DB']
# 创建数据表，用于存储代理IP
proxyTable = proxyDB['proxyIP']

# 代理 IP 爬取器
class CrawlProxyIP(object):
    def __init__(self, headers):
        print(u"[*] 开始执行代理池任务")
        self.headers = headers

    def delete_data(self, dict_data):
        '''
        数据删除
        :param dict_data: 数据字典
        '''
        proxyTable.delete_one(dict_data)
		
    def clean_data(self, list_index):
        '''
        数据清洗
        :param 需要进行重复性检查的字段列表
        通过 Mongo Shell 命令对数据库数据进行清洗，去除重复数据

        命令：
        db.test.aggregate([
            {
                $group: { _id: {公告标题: '$公告标题',项目编号: '$项目编号'},
                count: {$sum: 1},
                dups: {$addToSet: '$_id'}}
            },
            {
                $match: {count: {$gt: 1}}
            }
        ]).forEach(function(doc){
            doc.dups.shift();
            db.test.remove({_id: {$in: doc.dups}});
        })
        '''
        print("[+] 开始进行数据清洗")
        _id = {}
        for index in list_index:
            _id[str(index)] = '$' + str(index)

        pipeline = [
            {
                '$group': {
                    '_id': _id,
                    'count': {'$sum': 1},
                    'dups': {'$addToSet': '$_id'}
                },
            },
            {
                '$match': {'count': {'$gt': 1}}
            }
        ]

        try:
            map_id = map(lambda doc: doc['dups'][1:], proxyTable.aggregate(pipeline=pipeline))
            list_id = [item for sublist in map_id for item in sublist]
            list(map(lambda _id: self.delete_data({'_id': _id}), list_id))
            print("[+] 数据清洗完成")
        except Exception, e:
            print("[-] 数据清洗失败")
            print("ERROR: " + str(e.message))
		
    # 由于被网站封掉了 IP ，需要重构代码
    def crawl_ip(self):
        '''
        爬取网站的代理ip
        '''
        try:
            print(u"[*] 开始爬取代理 IP")
            url = configManager.url_proxy["proxyURL1"]
            for i in range(1000):
                timeout = 20
                socket.setdefaulttimeout(timeout)  # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
                sleep_download_time = 4
                time.sleep(sleep_download_time)

                proxyURL = url + "nn/{0}".format(i)
                # request = requests.get(proxyURL, headers=self.headers)
                # 根据协议类型，选择不同的代理
                ip_dict = [
                    {"http": "http://58.251.248.243:8118"},
                    {"http": "http://58.251.249.68:8118"},
                    {"http": "http://221.182.133.175:26997"},
                    {"https": "https://116.6.28.178:63000"},
                    {"https": "https://58.52.166.141:808"},
                ]

                # 获取页面信息
                proxies = random.choice(ip_dict)

                response = requests.get(proxyURL, headers=self.headers)

                selector = Selector(text=response.text)
                all_trs = selector.css("#ip_list tr")

                ip_list = []
                for tr in all_trs[1:]:
                    speed_str = tr.css(".bar::attr(title)").extract()[0]
                    if speed_str:
                        speed = float(speed_str.split("秒")[0])
                    all_texts = tr.css("td::text").extract()

                    ip = all_texts[0]
                    port = all_texts[1]
                    proxy_type = all_texts[5]

                    ip_list.append((ip, port, proxy_type, speed))

                for ip_info in ip_list:
                    proxyTable.insert_one({
                        'ip': ip_info[0],
                        'port': ip_info[1],
                        'proxy_type': ip_info[2],
                        'speed': ip_info[3]
                    })
                    print(u"[+] 存储成功 ip:{0}, port:{1}, proxy_type:{2}, speed:{3}".format(ip_info[0], ip_info[1], ip_info[2], ip_info[3]))
            print(u"[+] 爬取完成")
        except Exception, details:
            print(u"[-] 爬取失败")
            print("ERROR: " + str(details))

    # 新的代理ip网站
    @staticmethod
    def crawl_ip2(headers):
        '''
        爬取网站的代理ip
        '''
        # 创建数据表，用于存储代理IP
        proxyTable_Crawl = proxyDB['proxyIP']
        print(u"[*] 开始爬取代理IP")
        count = 1
        while count < 1000:
            try:
                # 页面是动态刷新的，所以设置爬取时间戳，间隔5秒
                # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置
                timeout = 20
                socket.setdefaulttimeout(timeout)
                sleep_download_time = 5
                time.sleep(sleep_download_time)

                url = configManager.url_proxy["proxyURL2"]

                # 根据协议类型，选择不同的代理
                ip_dict = [
                    {"http": "http://58.251.248.243:8118"},
                    {"http": "http://58.251.249.68:8118"},
                    {"http": "http://221.182.133.175:26997"},
                    {"https": "https://116.6.28.178:63000"},
                    {"https": "https://58.52.166.141:808"},
                ]

                # 获取页面信息
                proxies = random.choice(ip_dict)
                # response = requests.get(url, headers=headers)  # , proxies=proxies
                # html = response.text
                request = urllib2.Request(url=url, headers=headers)
                response = urllib2.urlopen(request)
                html = response.read()
                # 获取 IP
                content = etree.HTML(html)
                for i in range(1, 16):
                    pattern_xpath = "//ul[@class='l2'][{0}]".format(i)
                    node_list = content.xpath(pattern_xpath)
                    for node in node_list:
                        # 代理 IP
                        ip = node.xpath("./span/li")[0].text
                        # 代理 端口
                        port = node.xpath("./span/li")[1].text
                        # 代理 协议
                        protocol = node.xpath("./span/li")[3].text
                        # 响应时间
                        speed = node.xpath("./span/li")[7].text
                        print(u"协议：{0}  IP：{1}  端口：{2}  响应时间：{3}".format(str(protocol), str(ip), str(port),str(speed)))

                        # 字典形式存储
                        proxyTable_Crawl.insert_one({
                            'ip': ip,
                            'port': port,
                            'proxy_type': protocol,
                            'speed': speed
                        })
                        print(u"[+] 存储成功")
                count += 1
            except:
                count += 1
                # 取到空值就会跳过，并继续存储
                continue

# 代理 IP 自动化处理器
class IPOperator(object):
    def __init__(self, headers):
        self.headers = headers
        # 创建进程池，调用四个线程参与并行
        self.pool = Pool(processes=4)

    def delete_ip(self, ip, port, protocol):
        '''
        删除代理IP
        :param ip: 代理IP
        :param port: 代理端口
        :return:
        '''
        try:
            print("[*] 正在删除")
            proxyTable.delete_many({"ip": ip, "port": port, "proxy_type": protocol})
            print("[+] 删除成功")
        except Exception, e:
            print("[-] 删除失败")
            print("ERROR: " + str(e.message))

    def get_random_ip(self):
        '''
        从数据库中随机获取一个可以用的IP
        :return:返回字典类型的取值结果
        '''
        try:
            print("[*] 正在从数据库中随机获取代理IP")
            random_data = proxyTable.aggregate([{"$sample": {"size": 1}}])
            for data in random_data:
                ip = data["ip"].encode('utf-8')
                port = data["port"].encode('utf-8')
                protocol = data["proxy_type"].encode('utf-8')

                print("[+] 获取成功")

                random_ip = {
                    "ip": ip,
                    "port": port,
                    "protocol": protocol
                }
                print("[+] 随机IP为:  {0}:{1}:{2}".format(protocol, ip, port))
                return random_ip
        except Exception, e:
            print("[-] 获取失败")
            print("ERROR: " + str(e.message))

    def auto_dispose(self):
        '''
        自动化处理代理IP
        :return: 返回有效的代理IP数据流
        '''
        print("[*] 开始执行处理代理IP自动化流程")
        while True:
            try:
                random_ip = self.get_random_ip()
                valid_ip = {
                    "ip": random_ip["ip"],
                    "port": random_ip["port"],
                    "protocol": random_ip["protocol"]
                }
                print("[+] 处理完成")
                return valid_ip
            except:
                continue
