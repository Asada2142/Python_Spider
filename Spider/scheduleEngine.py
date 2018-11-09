#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/7 15:47
# File    : scheduleEngine.py
# Version : 2.0
# Describe: 调度引擎
# Update  :
        1.重构了调度引擎，可以实现全自动化爬取和推送。
'''
######## Import ########
import random
import time
import gc  # 内存释放
import os
import sys
import authentication  # 验证模块
import proxyPool  # 代理池
import configManager  # 配置管理器
import pageDownloader  # 网页下载器
import dataDisposer  # 数据处理器
import spiderLog  # 爬虫日志
import dataPusher  # 数据推送
import dataPush_HTML
import datetime
from retry import retry
from Lib import Console_Color
import log_record

######## Global Parameters ########
# 动态请求报头
HEADERS = {
    "User-Agent": random.choice(configManager.headers)
}
# URL 列表
URL_LIST = configManager.urlData
URL_LIST_ZB = configManager.urlData_ZB
# 数据库参数
DATABASE_PARAM = configManager.dataBaseParams
# 表的标题名
TABLE_TITLE = configManager.excel_table_title

# 全局逻辑控制器
LOGIC_RESPONSE = False
LOGIC_EXECUTE = False
LOGIC_DB_DISPOSE = False
LOGIC_DATA_PUSH = False
LOGIC_PUSH_DONE = False

# 有效的 URL
VALID_URL = []
# 有效的 URL 和对应代理
VALID_URL_PROXY = {}
# 关键词列表
KEY_WORD = []

# 获取当前文件名
CURRENT_PY = os.path.basename(sys.argv[0]).split(".")[0]
# 创建日志对象
LOG = spiderLog.SpiderLog(CURRENT_PY)
# 数据库
TENDER_TABLE = dataDisposer.DataOperate.dataOperate()

# 获取当前时间
DATE = dataDisposer.current_time()
TODAY_TIME = datetime.datetime(DATE.year, DATE.month, DATE.day, 0, 0, 0)
LOG_TIME = dataDisposer.current_time()

######## Engine Function ########

def proxy_engine(proxyOP):
    '''
    代理引擎
    :return: 返回代理 IP 字典，包含 ip、protocol、port
    '''
    LOG.info("[*] 开始执行代理引擎")
    try:
        LOG.info("[+] 获取代理")
        proxyDict = proxyOP.auto_dispose()
        print("-" * 25)
        print("[+] 当前代理")
        print("| Protocol: {0}".format(str(proxyDict["protocol"])))
        print("| IP:       {0}".format(str(proxyDict["ip"])))
        print("| Port:     {0}".format(str(proxyDict["port"])))
        print("-" * 25)
        return proxyDict
    except Exception, e:
        LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
    finally:
        del proxyOP
        gc.collect()

@retry(tries=5, delay=2)
def independent_proxy_engine(url):
    '''
    独立代理引擎，用于重新获取单个异常网页的代理
    :param url: 异常网页的 url 链接
    :return:
    '''
    LOG.info("[+] 开始重新获取代理")
    Console_Color.print_color(str="[*] 开始重新获取代理", forecolor="洋红")
    global VALID_URL_PROXY
    auth = authentication.Authentication(headers=HEADERS)
    proxyOP = proxyPool.IPOperator(headers=HEADERS)
    while True:
        proxyDict = proxy_engine(proxyOP)
        if auth.proxyVerify(url, proxyDict["protocol"], proxyDict["ip"], proxyDict["port"]):
            global VALID_URL_PROXY
            VALID_URL_PROXY[url] = proxyDict
            break

@retry(tries=5, delay=2)
def authentication_engine():
    '''
    验证引擎
    :param proxyDict: 代理 IP 字典
    :return: 通过验证后，赋值给响应逻辑器LOGIC_RESPONSE
    '''
    LOG.info("[*] 开始执行验证引擎")
    auth = authentication.Authentication(headers=HEADERS)
    # 避免每次创建对象都开辟块内存，调用四个进程池，特别占内存
    proxyOP = proxyPool.IPOperator(headers=HEADERS)
    global VALID_URL
    try:
        #### 验证 HTTP ####
        # 遍历 url 列表进行 http 验证请求，将有效的 url 存储在 VALID_URL 中
        LOG.info("[+] 验证 HTTP")  # 写入日志
        for url in URL_LIST.values():
            if auth.httpCodeVerify(url):
                VALID_URL.append(url)

        # 遍历新加入的 url 列表
        for url_zb in URL_LIST_ZB.values():
            if auth.httpCodeVerify(url_zb):
                VALID_URL.append(url_zb)

        # 遍历有效的 URL
        print("-" * 40)
        print("[+] 有效的 URL（{0}）".format(len(VALID_URL)))
        for valid_url in VALID_URL:
            print(str(valid_url))
        print("-" * 40)
    except Exception, e:
        LOG.error("[-] {0}".format(str(e.message)))  # 写入日志

    try:
        #### 验证代理 ####
        # 遍历有效的 url 列表
        LOG.info("[+] 验证代理")  # 写入日志
        for url in VALID_URL:
            # 循环取出代理进行代理验证，将有效的代理与对应的 url 存储在字典中
            while True:
                proxyDict = proxy_engine(proxyOP)
                if auth.proxyVerify(url, proxyDict["protocol"], proxyDict["ip"], proxyDict["port"]):
                    global VALID_URL_PROXY
                    VALID_URL_PROXY[url] = proxyDict
                    break
                # 每进行一次 url 的代理验证，释放一次内存
                gc.collect()

        # 遍历 VALID_URL_PROXY 字典
        print("-" * 40)
        print("[+] 有效网址和代理")
        for valid_url in VALID_URL_PROXY:
            protocol = VALID_URL_PROXY[valid_url]['protocol']
            ip = VALID_URL_PROXY[valid_url]['ip']
            port = VALID_URL_PROXY[valid_url]['port']
            print("{0}--({1}:{2}:{3})".format(valid_url, protocol, ip, port))
        print("-" * 40)

        # 存储完成，赋值全局变量
        global LOGIC_RESPONSE
        LOGIC_RESPONSE = True
    except Exception, e:
        LOG.error("[-] {0}".format(str(e.message)))  # 写入日志

    try:
        #### 验证数据库 ####
        LOG.info("[+] 验证数据库")
        if LOGIC_RESPONSE:
            global LOGIC_EXECUTE
            LOGIC_EXECUTE = auth.dataBaseVerify(DATABASE_PARAM)
    except Exception, e:
        LOG.error("[-] {0}".format(str(e.message)))  # 写入日志

    LOG.info("[+] 清理内存")
    # 删除 auth 和 proxyOP 对象
    del auth, proxyOP
    # 清理内存
    gc.collect()

TRY_NUM_ynsggzxxt_gc = 1
TRY_NUM_ynsggzxxt_zf = 1
TRY_NUM_ynsggzzw_gc = 1
TRY_NUM_kmsgg_zf = 1
TRY_NUM_kmsgg_gc = 1
TRY_NUM_ynszfcgw = 1
TRY_NUM_ynsggzxxt_gc_zb = 1
TRY_NUM_ynsggzxxt_zf_zb = 1
TRY_NUM_ynsggzzw_gc_zb = 1
TRY_NUM_ynsggzzw_zf_zb = 1
TRY_NUM_kmsgg_gc_zb = 1
TRY_NUM_kmsgg_zf_zb = 1
TRY_NUM_kmsgg_gc_by = 1
TRY_NUM_kmsgg_zf_by = 1
TRY_NUM_ynszfcgw_cg = 1

def page_engine():
    '''
    网页引擎
    '''
    LOG.info("[*] 开始执行网页引擎")
    downloader = pageDownloader.DownLoader(HEADERS)

    #### 招投标信息 ####

    def ynsggzxxt_gc():
        global TRY_NUM_ynsggzxxt_gc
        try:
            downloader.downloader_ynsggzxxt(
                URL_LIST['云南省公共资源交易中心电子服务系统_工程建设'],
                VALID_URL_PROXY[URL_LIST['云南省公共资源交易中心电子服务系统_工程建设']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynsggzxxt_gc))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynsggzxxt_gc += 1
            if TRY_NUM_ynsggzxxt_gc > 5:
                TRY_NUM_ynsggzxxt_gc = 1
                independent_proxy_engine(URL_LIST['云南省公共资源交易中心电子服务系统_工程建设'])
            ynsggzxxt_gc()

    def ynsggzxxt_zf():
        global TRY_NUM_ynsggzxxt_zf
        try:
            downloader.downloader_ynsggzxxt_zf(
                URL_LIST['云南省公共资源交易中心电子服务系统_政府采购'],
                VALID_URL_PROXY[URL_LIST['云南省公共资源交易中心电子服务系统_政府采购']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynsggzxxt_zf))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynsggzxxt_zf += 1
            if TRY_NUM_ynsggzxxt_zf > 5:
                TRY_NUM_ynsggzxxt_zf = 1
                independent_proxy_engine(URL_LIST['云南省公共资源交易中心电子服务系统_政府采购'])
            ynsggzxxt_zf()

    def ynsggzzw_gc():
        global TRY_NUM_ynsggzzw_gc
        try:
            downloader.downloader_ynsggzzw(
                URL_LIST['云南省公共资源交易中心网_工程建设'],
                VALID_URL_PROXY[URL_LIST['云南省公共资源交易中心网_工程建设']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynsggzzw_gc))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynsggzzw_gc += 1
            if TRY_NUM_ynsggzzw_gc > 5:
                TRY_NUM_ynsggzzw_gc = 1
                independent_proxy_engine(URL_LIST['云南省公共资源交易中心网_工程建设'])
            ynsggzzw_gc()

    def kmsgg_zf():
        global TRY_NUM_kmsgg_zf
        try:
            downloader.downloader_kmsgg(
                URL_LIST['昆明市公共资源交易中心网_政府采购'],
                VALID_URL_PROXY[URL_LIST['昆明市公共资源交易中心网_政府采购']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_kmsgg_zf))))  # 写入日志
            time.sleep(10)
            TRY_NUM_kmsgg_zf += 1
            if TRY_NUM_kmsgg_zf > 5:
                TRY_NUM_kmsgg_zf = 1
                independent_proxy_engine(URL_LIST['昆明市公共资源交易中心网_政府采购'])
            kmsgg_zf()

    def kmsgg_gc():
        global TRY_NUM_kmsgg_gc
        try:
            downloader.downloader_kmsgg_gc(
                URL_LIST['昆明市公共资源交易中心网_工程建设'],
                VALID_URL_PROXY[URL_LIST['昆明市公共资源交易中心网_工程建设']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_kmsgg_gc))))  # 写入日志
            time.sleep(10)
            TRY_NUM_kmsgg_gc += 1
            if TRY_NUM_kmsgg_gc > 5:
                TRY_NUM_kmsgg_gc = 1
                independent_proxy_engine(URL_LIST['昆明市公共资源交易中心网_工程建设'])
            kmsgg_gc()

    def ynszfcgw():
        global TRY_NUM_ynszfcgw
        try:
            downloader.downloader_ynszfcgw(
                URL_LIST['云南省政府采购网'],
                VALID_URL_PROXY[URL_LIST['云南省政府采购网']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynszfcgw))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynszfcgw += 1
            if TRY_NUM_ynszfcgw > 5:
                TRY_NUM_ynszfcgw = 1
                independent_proxy_engine(URL_LIST['云南省政府采购网'])
            ynszfcgw()


    #### 中标信息 ####
    def ynsggzxxt_gc_zb():
        global TRY_NUM_ynsggzxxt_gc_zb
        try:
            downloader.downloader_ynsggzxxt_gc_zb(
                URL_LIST_ZB['云南省公共资源交易信息网_工程建设_中标公告'],
                VALID_URL_PROXY[URL_LIST_ZB['云南省公共资源交易信息网_工程建设_中标公告']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynsggzxxt_gc_zb))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynsggzxxt_gc_zb += 1
            if TRY_NUM_ynsggzxxt_gc_zb > 5:
                TRY_NUM_ynsggzxxt_gc_zb = 1
                independent_proxy_engine(URL_LIST['云南省公共资源交易信息网_工程建设_中标公告'])
            ynsggzxxt_gc_zb()

    def ynsggzxxt_zf_zb():
        global TRY_NUM_ynsggzxxt_zf_zb
        try:
            downloader.downloader_ynsggzxxt_zf_zb(
                URL_LIST_ZB['云南省公共资源交易信息网_政府采购_中标结果'],
                VALID_URL_PROXY[URL_LIST_ZB['云南省公共资源交易信息网_政府采购_中标结果']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynsggzxxt_zf_zb))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynsggzxxt_zf_zb += 1
            if TRY_NUM_ynsggzxxt_zf_zb > 5:
                TRY_NUM_ynsggzxxt_zf_zb = 1
                independent_proxy_engine(URL_LIST['云南省公共资源交易信息网_政府采购_中标结果'])
            ynsggzxxt_zf_zb()

    def ynsggzzw_gc_zb():
        global TRY_NUM_ynsggzzw_gc_zb
        try:
            downloader.downloader_ynsggzzw_gc_zb(
                URL_LIST_ZB['云南省公共资源交易中心_工程建设_中标结果'],
                VALID_URL_PROXY[URL_LIST_ZB['云南省公共资源交易中心_工程建设_中标结果']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynsggzzw_gc_zb))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynsggzzw_gc_zb += 1
            if TRY_NUM_ynsggzzw_gc_zb > 5:
                TRY_NUM_ynsggzzw_gc_zb = 1
                independent_proxy_engine(URL_LIST['云南省公共资源交易中心_工程建设_中标结果'])
            ynsggzzw_gc_zb()

    def ynsggzzw_zf_zb():
        global TRY_NUM_ynsggzzw_zf_zb
        try:
            downloader.downloader_ynsggzzw_zf_zb(
                URL_LIST_ZB['云南省公共资源交易中心_政府采购_结果公示'],
                VALID_URL_PROXY[URL_LIST_ZB['云南省公共资源交易中心_政府采购_结果公示']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynsggzzw_zf_zb))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynsggzzw_zf_zb += 1
            if TRY_NUM_ynsggzzw_zf_zb > 5:
                TRY_NUM_ynsggzzw_zf_zb = 1
                independent_proxy_engine(URL_LIST['云南省公共资源交易中心_政府采购_结果公示'])
            ynsggzzw_zf_zb()

    def kmsgg_gc_zb():
        global TRY_NUM_kmsgg_gc_zb
        try:
            downloader.downloader_kmsgg_gc_zb(
                URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示'],
                VALID_URL_PROXY[URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_kmsgg_gc_zb))))  # 写入日志
            time.sleep(10)
            TRY_NUM_kmsgg_gc_zb += 1
            if TRY_NUM_kmsgg_gc_zb > 5:
                TRY_NUM_kmsgg_gc_zb = 1
                independent_proxy_engine(URL_LIST['昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示'])
            kmsgg_gc_zb()

    def kmsgg_zf_zb():
        global TRY_NUM_kmsgg_zf_zb
        try:
            downloader.downloader_kmsgg_zf_zb(
                URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_政府采购_结果公示'],
                VALID_URL_PROXY[URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_政府采购_结果公示']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_kmsgg_zf_zb))))  # 写入日志
            time.sleep(10)
            TRY_NUM_kmsgg_zf_zb += 1
            if TRY_NUM_kmsgg_zf_zb > 5:
                TRY_NUM_kmsgg_zf_zb = 1
                independent_proxy_engine(URL_LIST['昆明市公共资源交易平台公共服务系统_政府采购_结果公示'])
            kmsgg_zf_zb()

    def kmsgg_gc_by():
        global TRY_NUM_kmsgg_gc_by
        try:
            downloader.downloader_kmsgg_gc_by(
                URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_工程建设_补遗通知'],
                VALID_URL_PROXY[URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_工程建设_补遗通知']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_kmsgg_gc_by))))  # 写入日志
            time.sleep(10)
            TRY_NUM_kmsgg_gc_by += 1
            if TRY_NUM_kmsgg_gc_by > 5:
                TRY_NUM_kmsgg_gc_by = 1
                independent_proxy_engine(URL_LIST['昆明市公共资源交易平台公共服务系统_工程建设_补遗通知'])
            kmsgg_gc_by()

    def kmsgg_zf_by():
        global TRY_NUM_kmsgg_zf_by
        try:
            downloader.downloader_kmsgg_zf_by(
                URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_政府采购_补遗通知'],
                VALID_URL_PROXY[URL_LIST_ZB['昆明市公共资源交易平台公共服务系统_政府采购_补遗通知']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_kmsgg_zf_by))))  # 写入日志
            time.sleep(10)
            TRY_NUM_kmsgg_zf_by += 1
            if TRY_NUM_kmsgg_zf_by > 5:
                TRY_NUM_kmsgg_zf_by = 1
                independent_proxy_engine(URL_LIST['昆明市公共资源交易平台公共服务系统_政府采购_补遗通知'])
            kmsgg_zf_by()

    def ynszfcgw_cg():
        global TRY_NUM_ynszfcgw_cg
        try:
            downloader.downloader_ynszfcgw_cg(
                URL_LIST_ZB['云南省政府采购网_采购结果'],
                VALID_URL_PROXY[URL_LIST_ZB['云南省政府采购网_采购结果']])
        except Exception, e:
            LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
            LOG.error("[-] {0}".format(str("Trying times: {0}".format(TRY_NUM_ynszfcgw_cg))))  # 写入日志
            time.sleep(10)
            TRY_NUM_ynszfcgw_cg += 1
            if TRY_NUM_ynszfcgw_cg > 5:
                TRY_NUM_ynszfcgw_cg = 1
                independent_proxy_engine(URL_LIST['云南省政府采购网_采购结果'])
            ynszfcgw_cg()


    global LOGIC_DB_DISPOSE
    LOG.info("[+] 抓取数据")
    print("[*] 开始抓取招投标信息..")
    #### 招投标信息 ####
    ynsggzxxt_gc()
    ynsggzxxt_zf()
    ynsggzzw_gc()
    kmsgg_zf()
    kmsgg_gc()
    ynszfcgw()

    print("[*] 开始抓取中标信息..")
    #### 中标信息 ####
    ynsggzxxt_gc_zb()
    ynsggzxxt_zf_zb()
    ynsggzzw_gc_zb()
    ynsggzzw_zf_zb()
    kmsgg_gc_zb()
    kmsgg_zf_zb()
    kmsgg_gc_by()
    kmsgg_zf_by()
    ynszfcgw_cg()

    LOG.info("[+] 抓取完成")
    # del downloader
    gc.collect()
    LOGIC_DB_DISPOSE = True

def db_engine():
    '''
    数据库引擎
    '''
    LOG.info("[*] 开始执行数据库引擎")
    # 创建数据处理对象
    #### 招投标数据 ####
    ynsggzxxt = dataDisposer.DataStore('ynsggzxxt')
    ynsggzzw = dataDisposer.DataStore('ynsggzzw')
    kmsgg = dataDisposer.DataStore('kmsgg')
    kmsgg_gc = dataDisposer.DataStore('kmsgg_gc')
    ynsggzxxt_zf = dataDisposer.DataStore('ynsggzxxt_zf')
    ynszfcgw = dataDisposer.DataStore('ynszfcgw')

    #### 中标数据 ####
    ynsggzxxt_gc_zb = dataDisposer.DataStore('ynsggzxxt_gc_zb')
    ynsggzxxt_zf_zb = dataDisposer.DataStore('ynsggzxxt_zf_zb')

    ynsggzzw_gc_zb = dataDisposer.DataStore('ynsggzzw_gc_zb')
    ynsggzzw_zf_zb = dataDisposer.DataStore('ynsggzzw_zf_zb')

    kmsgg_gc_zb = dataDisposer.DataStore('kmsgg_gc_zb')
    kmsgg_zf_zb = dataDisposer.DataStore('kmsgg_zf_zb')
    kmsgg_gc_by = dataDisposer.DataStore('kmsgg_gc_by')
    kmsgg_zf_by = dataDisposer.DataStore('kmsgg_zf_by')

    ynszfcgw_cg = dataDisposer.DataStore('ynszfcgw_cg')

    global LOGIC_DATA_PUSH
    try:
        LOG.info("[+] 数据库处理中")
        #### 数据操作 ####

        ## 招投标数据 ##
        ## 云南省公共资源交易中心电子服务系统
        ynsggzxxt.clean_data(['公告标题', '项目编号'])  # 数据清洗（去重）
        ynsggzxxt.update_date_by_time('截止时间')  # 数据更新（时间）
        ynsggzxxt.delete_none_data()

        ## 云南省公共资源交易中心网（旧）
        ynsggzzw.clean_data(['公告标题', '项目编号'])   # 数据清洗（去重）
        ynsggzzw.delete_none_data()

        ## 昆明市公共资源交易中心网
        kmsgg.clean_data(['编号', '工程名称'])  # 数据清洗（去重）
        kmsgg.update_date_by_time("结束时间")  # 数据更新（时间）
        kmsgg.delete_none_data()

        ## 昆明市公共资源交易中心网_工程
        kmsgg_gc.clean_data(['编号', '工程名称'])  # 数据清洗（去重）
        kmsgg_gc.update_date_by_time("结束时间")  # 数据更新（时间）
        kmsgg_gc.delete_none_data()

        ## 云南省公共资源交易中心电子服务系统_政府
        ynsggzxxt_zf.clean_data(['公告标题', '项目编号'])  # 数据清洗（去重）
        ynsggzxxt_zf.update_date_by_time('截止时间')  # 数据更新（时间）
        ynsggzxxt_zf.delete_none_data()

        ## 云南省政府采购网
        ynszfcgw.clean_data(['编号', '工程名称'])  # 数据清洗（去重）
        ynszfcgw.delete_none_data()

        ## 中标数据 ##
        # 云南省公共资源交易信息网_工程建设_中标公告
        ynsggzxxt_gc_zb.clean_data(['项目名称', '发布时间'])
        ynsggzxxt_gc_zb.delete_none_data()
        # 云南省公共资源交易信息网_政府采购_中标结果
        ynsggzxxt_zf_zb.clean_data(['项目名称', '发布时间'])
        ynsggzxxt_zf_zb.delete_none_data()

        # 云南省公共资源交易中心_工程建设_中标结果
        ynsggzzw_gc_zb.clean_data(['公告标题', '发布时间'])
        ynsggzzw_gc_zb.delete_none_data()
        # 云南省公共资源交易中心_政府采购_结果公示
        ynsggzzw_zf_zb.clean_data(['公告标题', '发布时间'])
        ynsggzzw_zf_zb.delete_none_data()

        # 昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示
        kmsgg_gc_zb.clean_data(['编号', '工程名称'])
        kmsgg_gc_zb.delete_none_data()
        # 昆明市公共资源交易平台公共服务系统_政府采购_结果公示
        kmsgg_zf_zb.clean_data(['编号', '工程名称'])
        kmsgg_zf_zb.delete_none_data()
        # 昆明市公共资源交易平台公共服务系统_工程建设_补遗通知
        kmsgg_gc_by.clean_data(['编号', '工程名称'])
        kmsgg_gc_by.delete_none_data()
        # 昆明市公共资源交易平台公共服务系统_政府采购_补遗通知
        kmsgg_zf_by.clean_data(['编号', '工程名称'])
        kmsgg_zf_by.delete_none_data()

        # 云南省政府采购网_采购结果
        ynszfcgw_cg.clean_data(['编号', '工程名称'])
        ynszfcgw_cg.delete_none_data()

        ##################
        LOG.info("[+] 数据库处理完成")
        LOGIC_DATA_PUSH = True
    except Exception, e:
        LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
        LOGIC_DATA_PUSH = False
    finally:
        # 删除对象，释放内存
        del ynsggzxxt, ynsggzzw, kmsgg #, ynsggzxxt_zb, ynsggzzw_zb, ynstz_zb, kmsgg_zb
        gc.collect()

def data_push_engine():
    '''
    数据推送引擎
    :return:
    '''
    LOG.info("[*] 开始执行数据推送引擎")
    #### 初始化数据写入模块 ####
    writer = dataPusher.DataWrite()
    html_push = dataPush_HTML.HTML_Content()

    # 云南省公共资源交易中心电子服务系统 'ynsggzxxt'
    # 云南省公共资源交易中心电子服务系统_政府采购 'ynsggzxxt_zf'
    # 云南省公共资源交易中心网 'ynsggzzw'
    # 昆明市公共资源交易中心网 'kmsgg'
    # 昆明市公共资源交易中心网_工程建设 'kmsgg_gc'
    # 云南省政府采购网 'ynszfcgw'
    #  table_name = ['ynsggzxxt', 'ynsggzzw', 'kmsgg', 'kmsgg_gc', 'ynsggzxxt_zf', 'ynszfcgw', ] #'ynsggzxxt_zb', 'ynsggzzw_zb', 'ynstz_zb', 'kmsgg_zb']
    list_file_path = []

    try:
        #----------- 旧方法 -----------#
        # # 遍历表
        # for table in table_name:
        #     list_data = get_data(table)
        #     header_data = configManager.excel_header_data[table]
        #     # header_data_zb = configManager.excel_header_data_zb[table]
        #
        #     # 读取关键词文件并生成关键字列表
        #     with open(r".\keyword_file\keyword.txt", 'r') as f:
        #         line = f.read()
        #         if line not in KEY_WORD:
        #             KEY_WORD.append(line)
        #     key_word = str(KEY_WORD[0]).split('\n')
        #
        #     # 筛选关键词信息
        #     list_data_parse = []
        #     for data in list_data:
        #         for key in key_word:
        #             # 获取每张表对应的标题字段并判断是否包含关键词信息
        #             if key in data[TABLE_TITLE[table]] and data not in list_data_parse:
        #                 list_data_parse.append(data)
        #
        #     # 判断当天数据是否为空
        #     # 写入两个 excel 文本（招投标）
        #     if len(list_data) != 0:
        #         file_path = writer.excel_write(
        #             excel_sheet_name=configManager.excel_data_name[table],
        #             excel_head_data=header_data,
        #             excel_data=list_data,
        #             logic_file_type=0
        #         )
        #
        #     if len(list_data_parse) != 0:
        #         file_path_parse = writer.excel_write_parse(
        #             excel_sheet_name=configManager.excel_data_name[table],
        #             excel_head_data=header_data,
        #             excel_data=list_data_parse,
        #             logic_file_type=1
        #         )
        #
        #     # 写入两个 excel 文本（中标）
        #     # file_path_zb = writer.excel_write(excel_sheet_name=configManager.excel_data_name_zb[table], excel_head_data=header_data_zb, excel_data=dict_data, logic_file_type=2)
        #     # file_path_parse_zb = writer.excel_write(excel_sheet_name=configManager.excel_data_name_zb[table], excel_head_data=header_data_zb, excel_data=dict_data_parse, logic_file_type=3)
        # ---------------------------#


        LOG.info("[+] 正在写入文件...")
        file_path = html_push.html_write(
            title="招投标信息",
            name="今日份的招投标文件",
            dict_html_data_name=configManager.ztb_data_name,
            logic_file_type=0
        )

        file_path_parse = html_push.html_write_keywords(
            title="招投标信息",
            name="今日份的招投标文件（关键词筛选）",
            dict_html_data_name=configManager.ztb_data_name,
            logic_file_type=1
        )

        file_path_zb = html_push.html_write(
            title="中标信息",
            name="今日份的中标文件",
            dict_html_data_name=configManager.zb_data_name,
            logic_file_type=2
        )

        file_path_parse_zb = html_push.html_write_keywords(
            title="中标信息",
            name="今日份的中标文件（关键词筛选）",
            dict_html_data_name=configManager.zb_data_name,
            logic_file_type=3
        )

        # 遍历路径添加到路径列表中
        if file_path != "":
            if file_path not in list_file_path:
                list_file_path.append(file_path)

        if file_path_parse != "":
            if file_path_parse not in list_file_path:
                list_file_path.append(file_path_parse)

        if file_path_zb != "":
            if file_path_zb not in list_file_path:
                list_file_path.append(file_path_zb)

        if file_path_parse_zb != "":
            if file_path_parse_zb not in list_file_path:
                list_file_path.append(file_path_parse_zb)

        LOG.info("[+] 写入完成")
    except Exception, e:
        LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
    finally:
        # 删除对象，释放内存
        del writer
        gc.collect()

    #### 初始化数据推送模块 ####
    LOG.info("[+] 正在推送数据...")
    pusher = dataPusher.DataSend()
    try:
        if len(list_file_path) != 0:
            content = """
            自动化爬虫
            版本：5.1
            当前时间：{0}
            开发语言：Python 2.7
            数据库：MongoDB 3.6.5
            平台：Windows Server 2012 Data Center
			版本更新：
				1.优化了爬取算法，提高了推送成功率，出现断电的情况会进行补充推送。
					
			如有任何问题和建议，请联系开发者：xxxxxxxxx@qq.com
            """.format(dataDisposer.current_time())
        else:
            content = """
            爬虫提示：今天没有推送的数据哦
					
			自动化爬虫
            版本：5.1
            当前时间：{0}
            开发语言：Python 2.7
            数据库：MongoDB 3.6.5
            平台：Windows Server 2012 Data Center
            版本更新：
				1.优化了爬取算法，提高了推送成功率，出现断电的情况会进行补充推送。
					
			如有任何问题和建议，请联系开发者：xxxxxxxxx@qq.com
            """.format(dataDisposer.current_time())
        global LOGIC_PUSH_DONE
        # 将附件添加到文本中
        if pusher.send_mail(content, list_file_path):
            LOGIC_PUSH_DONE = True
        else:
            LOGIC_PUSH_DONE = False
        LOG.info("[+] 推送完成")
	log_record.log_recorder(LOG_TIME, "执行成功")
    except Exception, e:
        LOG.error("[-] {0}".format(str(e.message)))  # 写入日志
	log_record.log_recorder(LOG_TIME, "执行失败")
    finally:
        # 删除对象，释放内存
        del pusher
        gc.collect()

def get_data(table_name):
    '''
    数据获取函数
    :param table_name: 表名
    :return: 返回数据列表
    '''
    tenderTable = TENDER_TABLE[table_name]
    # 获取今日数据
    list_data = list(tenderTable.find(
        {
            '发布时间': {"$gte": TODAY_TIME},
            '推送': False
        })
    )
    tenderTable.update(
        {'推送': False},
        {'$set': {'推送': True}},
        multi=True,
        upsert=True
    )
    return list_data

def current_time_parse():
    '''
    获取当前时间，返回小时和分钟
    :return: 当前小时和分钟
    '''
    current_date = dataDisposer.current_time()
    current_hour = current_date.hour
    current_minute = current_date.minute
    return current_hour, current_minute

######## Main Function ########
def main():
    print("-" * 40)
    print("[*] 开始执行爬虫程序")
    print("[+] 版本：5.1")
    print("-" * 40)
    time.sleep(2)

    # 验证代理和网页请求返回值
    authentication_engine()

    # 如果验证执行完毕，开始执行网页引擎
    if LOGIC_EXECUTE:
        page_engine()

    # 如果网页引擎执行完毕，开始执行数据库引擎
    if LOGIC_DB_DISPOSE:
        db_engine()

    # 如果数据库引擎执行完毕，开始执行数据推送引擎
    if LOGIC_DATA_PUSH:
        data_push_engine()

    # 如果数据推送引擎执行完毕，则关闭整个引擎
    if LOGIC_PUSH_DONE:
       print("[+] 爬虫执行完成，引擎关闭")

######## Start Execute ########
if __name__ == "__main__":
    start = time.clock()
    main()
    end = time.clock()
    print ("[+] 执行消耗时长：{0}".format(end - start))
