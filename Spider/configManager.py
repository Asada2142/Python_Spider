#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:03
# File    : configManager.py
# Version : 1.0
# Describe: 配置管理器
# Update  :
'''

url_proxy = {
        "proxyURL1": "http://www.xicidaili.com/",  # 代理 IP 网站
        "proxyURL2": "http://www.data5u.com/free/gngn/index.shtml"  # 代理 IP 网站
}

headers = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",  # IE
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",  # Chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",  # Firefox
        "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintoshl Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",  # Opera
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11"
]

dataBaseParams = {
        # mongodb 参数
        "userName": "localhost",
        "port": 27017,
        "dataBaseName": "Tender_DB",
        "logBaseName": "Spider_Log"
}

table_title = {
        "ynsggzxxt": u"公告标题",
        "ynsggzxxt_zf": u"公告标题",

        "ynsggzzw": u"公告标题",

        "kmsgg": u"工程名称",
        "kmsgg_gc": u"工程名称",

        "ynszfcgw": u"工程名称",

        "ynsggzxxt_gc_zb": u"公告名称",
        "ynsggzxxt_zf_zb": u"公告名称",

        "ynsggzzw_gc_zb": u"公告标题",
        "ynsggzzw_zf_zb": u"公告标题",

        "kmsgg_gc_zb": u"工程名称",
        "kmsgg_zf_zb": u"工程名称",
        "kmsgg_gc_by": u"工程名称",
        "kmsgg_zf_by": u"工程名称",

        "ynszfcgw_cg": u"工程名称",
}

########################
#### 招标结果配置信息 ####
########################
urlData = {
        "云南省公共资源交易中心电子服务系统_工程建设": "https://www.ynggzyxx.gov.cn/jyxx/jsgcZbgg",
        "云南省公共资源交易中心电子服务系统_政府采购": "https://www.ynggzyxx.gov.cn/jyxx/zfcg/cggg",

        "云南省公共资源交易中心网_工程建设": "https://www.ynggzy.com/jyxx/jsgcZbgg",
        "云南省公共资源交易中心网_政府采购": "https://www.ynggzy.com/jyxx/zfcg/cggg",

        "昆明市公共资源交易中心网_政府采购": "https://www.kmggzy.com/Jyweb/JYXTXXList.aspx?Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&SubType=2",
        "昆明市公共资源交易中心网_工程建设": "https://www.kmggzy.com/Jyweb/ZBGGList.aspx?Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&SubType=1&SubType2=1",

        "云南省政府采购网": "http://www.yngp.com/bulletin.do?method=moreList&menuSelect=nav2"
}

ztb_data_name = {
        "ynsggzxxt": u"云南省公共资源交易中心电子服务系统_工程建设",
        "ynsggzxxt_zf": u"云南省公共资源交易中心电子服务系统_政府采购",

        "ynsggzzw": u"云南省公共资源交易中心网",

        "kmsgg": u"昆明市公共资源交易中心网_政府采购",
        "kmsgg_gc": u"昆明市公共资源交易中心网_工程建设",

        "ynszfcgw": u"云南省政府采购网"
}

########################
#### 中标结果配置信息 ####
########################
urlData_ZB = {
        "云南省公共资源交易信息网_工程建设_中标公告": "https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggs",
        "云南省公共资源交易信息网_政府采购_中标结果": "https://www.ynggzyxx.gov.cn/jyxx/zfcg/zbjggs?area=000&secondArea=",

        "云南省公共资源交易中心_工程建设_中标结果": "https://www.ynggzy.com/jyxx/jsgcZbjggs",
        "云南省公共资源交易中心_政府采购_结果公示": "https://www.ynggzy.com/jyxx/zfcg/zbjggs?area=000&secondArea=",

        "昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示": "https://www.kmggzy.com/Jyweb/PBJGGSList.aspx?Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&SubType=1&SubType2=11",
        "昆明市公共资源交易平台公共服务系统_政府采购_结果公示": "https://www.kmggzy.com/Jyweb/JYXTXXList.aspx?Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&SubType=2&SubType2=14",
        "昆明市公共资源交易平台公共服务系统_工程建设_补遗通知": "https://www.kmggzy.com/Jyweb/JYXTXXList.aspx?Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&SubType=1&SubType2=2",
        "昆明市公共资源交易平台公共服务系统_政府采购_补遗通知": "https://www.kmggzy.com/Jyweb/JYXTXXList.aspx?Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&SubType=2&SubType2=13",

        "云南省政府采购网_采购结果": "http://www.yngp.com/bulletin.do?method=moreList&menuSelect=nav2"
}

zb_data_name = {
        "ynsggzxxt_gc_zb": u"云南省公共资源交易信息网_工程建设_中标公告",
        "ynsggzxxt_zf_zb": u"云南省公共资源交易信息网_政府采购_中标结果",

        "ynsggzzw_gc_zb": u"云南省公共资源交易中心_工程建设_中标结果",
        "ynsggzzw_zf_zb": u"云南省公共资源交易中心_政府采购_结果公示",

        "kmsgg_gc_zb": u"昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示",
        "kmsgg_zf_zb": u"昆明市公共资源交易平台公共服务系统_政府采购_结果公示",
        "kmsgg_gc_by": u"昆明市公共资源交易平台公共服务系统_工程建设_补遗通知",
        "kmsgg_zf_by": u"昆明市公共资源交易平台公共服务系统_政府采购_补遗通知",

        "ynszfcgw_cg": u"云南省政府采购网_采购结果"
}
