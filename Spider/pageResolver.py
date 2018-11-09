#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:04
# File    : pageResolver.py
# Version : 1.1
# Describe: 网页解析器
# Update  :
        1.增加了中标网页的解析方法
'''

import re
from lxml import etree
import datetime
import sys
from retry import retry
import configManager
import random
import urllib2
# 设置默认编码，防止出现中文字符乱码
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

HEADERS = {
    "User-Agent": random.choice(configManager.headers)
}

class Resolver(object):
    def time_parse(self, currentTime):
        '''
        获取系统当前时间，返回规约后的时间信息
        :param currentTime: 当前时间（字符串类型）
        :return:当前时间（时间类型）
        '''
        date = datetime.datetime.strptime(currentTime, '%Y-%m-%d')
        return date

    #### 招投标数据 ####

    @retry(tries=3, delay=2)
    def resovler_ynsggzxxt(self, html, page_num):
        '''
        云南省公共资源交易中心电子服务系统解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        # 获取招标信息
        xpathPattern = "//div/table[@id='data_tab']/tbody/tr"

        # 通过 xpath 返回符合匹配的结果列表
        node_list = text.xpath(xpathPattern)

        # 正则规约字段
        strParse = re.compile("\s")

        # 遍历结果列表
        for node in node_list:
            # 筛除标题的空值标签
            if len(node.xpath("./td")) > 0:
                # 项目编号
                projectNumber = node.xpath("./td")[1].text

                # 公告标题（正则规约）
                title = strParse.sub("", node.xpath("./td/a")[0].text)

                # 发布时间
                startTime = node.xpath("./td")[3].text
                start_time = self.time_parse(startTime)

                # 截止时间
                endTime = node.xpath("./td")[4].text
                end_time = self.time_parse(endTime)

                # 状态（正则规约）
                status = strParse.sub("", node.xpath("./td")[5].text)

                # 判断状态是否为空，如果为空，则跳转到下一级标签 i
                if status is "":
                    status = strParse.sub("", node.xpath("./td/i")[0].text)

                # href 链接地址
                href = "https://www.ynggzyxx.gov.cn" + str(node.xpath("./td/a/@href")[0])

                # 存储到字典
                resolveMessage = {
                    "项目编号": projectNumber,
                    "公告标题": title,
                    "发布时间": start_time,
                    "截止时间": end_time,
                    "状态": status,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)
    def resovler_ynsggzzw(self, html, page_num):
        '''
        云南省公共资源交易中心网解析器
        :param html:
        :param page_num:
        :return:
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 获取招标信息
        xpathPattern = "//table[@id='data_tab']/tbody/tr"

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        # 通过 xpath 返回符合匹配的结果列表
        node_list = text.xpath(xpathPattern)

        # 正则规约字段
        strParse = re.compile("\s")

        # 遍历结果列表
        for node in node_list:
            # 筛除标题的空值标签
            if len(node.xpath("./td")) > 0:
                # 序号
                serialNumber = node.xpath("./td")[0].text

                # 项目编号
                projectNumber = node.xpath("./td")[1].text

                # href 链接地址
                href = "https://www.ynggzyxx.gov.cn" + str(node.xpath("./td/a/@href")[0])

                # 发布时间
                startTime = node.xpath("./td")[3].text
                start_time = self.time_parse(startTime)

                # 公告标题（正则规约）
                title = strParse.sub("", node.xpath("./td/a")[0].text)

                # 存储到字典
                resolveMessage = {
                    "项目编号": projectNumber,
                    "公告标题": title,
                    "发布时间": start_time,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)
    def resovler_kmsgg(self, html, page_num):
        '''
        昆明市公共资源交易中心网解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        node_list = text.xpath("//div[@class='zb_from']/table/tbody/tr")
        for i in range(1, 16):
            # 编号
            num = node_list[i].xpath("./td")[1].text

            # 工程名称
            project_name = (node_list[i].xpath("./@field_bdmcggbt")[0]).encode('utf8')

            # 链接
            href = "https://www.kmggzy.com/Jyweb/" + str(node_list[i].xpath("./td/a/@href")[0])

            start_time = None
            # 起始时间
            startTime = node_list[i].xpath("./td")[3].text
            if startTime is not None:
                start_time = self.time_parse(startTime)

            end_time = None
            # 结束时间
            endTime = node_list[i].xpath("./td")[4].text
            if endTime is not None:
                end_time = self.time_parse(endTime)

            status = None
            # 状态
            if node_list[i].xpath("./td")[5].text is not None:
                status = (node_list[i].xpath("./td")[5].text).encode('utf8')

            # 存储到字典
            if num and project_name and start_time and end_time and status is not None:
                resolveMessage = {
                    "编号": num,
                    "工程名称": project_name,
                    "发布时间": start_time,
                    "结束时间": end_time,
                    "状态": status,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)
    def resovler_kmsgg_gc(self, html, page_num):
        '''
        昆明市公共资源交易中心网解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        node_list = text.xpath("//div[@class='zb_from']/table/tbody/tr")
        for i in range(1, 16):
            # 编号
            num = node_list[i].xpath("./td")[1].text

            # 工程名称
            project_name = (node_list[i].xpath("./@field_bdmcggbt")[0]).encode('utf8')

            # 链接
            href = "https://www.kmggzy.com/Jyweb/" + str(node_list[i].xpath("./td/a/@href")[0])

            start_time = None
            # 起始时间
            startTime = node_list[i].xpath("./td")[3].text
            if startTime is not None:
                start_time = self.time_parse(startTime)

            end_time = None
            # 结束时间
            endTime = node_list[i].xpath("./td")[4].text
            if endTime is not None:
                end_time = self.time_parse(endTime)

            status = None
            # 状态
            if node_list[i].xpath("./td")[5].text is not None:
                status = (node_list[i].xpath("./td")[5].text).encode('utf8')

            # 存储到字典
            if num and project_name and start_time and end_time and status is not None:
                resolveMessage = {
                    "编号": num,
                    "工程名称": project_name,
                    "发布时间": start_time,
                    "结束时间": end_time,
                    "状态": status,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)
    def resovler_ynsggzxxt_zf(self, html, page_num):
        '''
        云南省公共资源交易中心电子服务系统解析器 政府采购
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        # 获取招标信息
        xpathPattern = "//div/table[@id='data_tab']/tbody/tr"

        # 通过 xpath 返回符合匹配的结果列表
        node_list = text.xpath(xpathPattern)

        # 正则规约字段
        strParse = re.compile("\s")

        # 遍历结果列表
        for node in node_list:
            # 筛除标题的空值标签
            if len(node.xpath("./td")) > 0:
                # 项目编号
                projectNumber = node.xpath("./td")[1].text

                # 公告标题（正则规约）
                title = strParse.sub("", node.xpath("./td/a")[0].text)

                # 发布时间
                startTime = node.xpath("./td")[3].text
                start_time = self.time_parse(startTime)

                # 截止时间
                endTime = node.xpath("./td")[4].text
                end_time = self.time_parse(endTime)

                # 状态（正则规约）
                status = strParse.sub("", node.xpath("./td")[5].text)

                # 判断状态是否为空，如果为空，则跳转到下一级标签 i
                if status is "":
                    status = strParse.sub("", node.xpath("./td/i")[0].text)

                # href 链接地址
                href = "https://www.ynggzyxx.gov.cn" + str(node.xpath("./td/a/@href")[0])

                # 存储到字典
                resolveMessage = {
                    "项目编号": projectNumber,
                    "公告标题": title,
                    "发布时间": start_time,
                    "截止时间": end_time,
                    "状态": status,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)

        return resolveResult

    @retry(tries=3, delay=2)
    def resovler_ynszfcgw(self, html, page_num):
        '''
        云南省政府采购网
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)
        for i in range(0, 10):
            node_list = text.xpath("//tr[@data-row-id='{0}']".format(i))

            for node in node_list:
                text_total = node.xpath('./td')[0].xpath('./a')[0].text

                # 编号
                num = text_total[:text_total.find('：')]

                # 工程名称
                project_name = text_total[text_total.find('：') + 1:]

                # 区划
                area = node.xpath('./td')[2].text

                time_push = None
                # 发布时间
                timePush = node.xpath('./td')[3].text
                if timePush is not None:
                    time_push = self.time_parse(timePush)

                # 链接
                cursor = node.xpath('./td')[0].xpath('./a/@data-bulletin_id')[0]

                href = "http://www.yngp.com/newbulletin_zz.do?method=preinsertgomodify&operator_state=1&flag=view&bulletin_id={0}".format(
                    cursor)

                # 存储到字典
                if num and project_name and area and href and time_push is not None:
                    resolveMessage = {
                        "编号": num,
                        "工程名称": project_name,
                        "发布时间": time_push,
                        "区划": area,
                        "链接": href,
                        "推送": False
                    }
                    resolveResult.append(resolveMessage)
        return resolveResult

    #### 中标数据 ####
    @retry(tries=3, delay=2)
    def get_url(self, url, proxy_dict):
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        proxy_handler = urllib2.ProxyHandler({proxyProtocol: "{0}:{1}".format(proxyIP, proxyPort)})

        opener_proxy = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener_proxy)
        request = urllib2.Request(url=url, headers=HEADERS)
        response = urllib2.urlopen(request)
        html = response.read()

        return html

    @retry(tries=3, delay=2)  # 70%
    def resovler_ynsggzxxt_gc_zb(self, html, page_num, proxy_dict):
        '''
        云南省公共资源交易信息网_工程建设_中标公告解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        def resolve_pp_0(html):
            try:
                people = ''
                price = 0.0
                text = etree.HTML(html)
                node_second_list = text.xpath("//div[@class='con']//tr")
                for node_second in node_second_list:
                    if "中标人：" == node_second.xpath("./td")[0].text:
                        people = node_second.xpath("./td")[1].xpath('./b//span')[0].text
                    if "中标价" in node_second.xpath("./td")[0].text:
                        totalCount = node_second.xpath("./td")[1].xpath('./b//span')[0].text
                        price = float(re.sub("\D", "", totalCount))
                return people, price
            except:
                return None, 0.0

        def resolve_pp_1(html):
            '''
            子网页解析器_1
            eg: https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggsDetail?guid=7befec50-6cf1-49b1-a5ec-b3b1cf6d3ab2&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                people = ''
                price = 0.0
                text = etree.HTML(html)
                xpathPattern = "//div[@class='w1200s']//table"
                node_list = text.xpath(xpathPattern)[0]
                for index, node in enumerate(node_list):
                    if index == 7:
                        people = node.xpath('./td//tr')[1].xpath('./td')[1].text
                        price_tmp = node.xpath('./td//tr')[1].xpath('./td')[6].text
                        if price_tmp == 0 or price_tmp == '/':
                            price = float(0.0)
                # print("中标人： {0}，中标价：{1}".format(people, price))
                return people, price
            except:
                return None, 0.0

        def resolve_pp_2(html):
            '''
            子网页解析器_2
            eg: https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggsDetail?guid=2ab5a6f5-30e2-4599-846b-22597815e3dd&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                people = ''
                price = 0.0
                text = etree.HTML(html)
                xpathPattern = "//div[@class='w1200s']//div[@class='detail_contect']//p"
                node_list = text.xpath(xpathPattern)
                for node in node_list:
                    if "第一中标候选人" in node.text:
                        people_tmp = str(node.text).strip()
                        people = people_tmp[people_tmp.find('：') + 3:]
                    elif "投标报价" in node.text:
                        price_tmp = node.xpath('./span')[0].text
                        price = float(price_tmp)
                # print("中标人： {0}，中标价：{1}".format(people, price))
                return people, price
            except:
                return None, 0.0

        def resolve_pp_3(html):
            '''
            子网页解析器_3
            eg: https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggsDetail?guid=e145f187-b9d9-4573-b4b0-f5c4c66ddbdb&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                people = ''
                price = 0.0
                text = etree.HTML(html)
                xpathPattern = "//div[@class='w1200s']//div[@class='page_contect bai_bg']//tr"
                node_list = text.xpath(xpathPattern)
                for node in node_list:
                    ## 中标人
                    tmp = node.xpath('./td//span')[0].text
                    if "第一中标候选人" == tmp:
                        people = node.xpath('./td//span')[1].text

                    ## 中标价格
                    node_td = node.xpath('./td')
                    if len(node_td) > 3:
                        for no in node_td:
                            if len(no.xpath('./span')) > 0 and "中标价（万元）" == no.xpath('./span')[0].text:
                                price = float(node_td[3].xpath('./span')[0].text)
                # print("中标人： {0}，中标价：{1}".format(people, price))
                return people, price
            except:
                return None, 0.0

        def resolve_pp_4(html):
            '''
            子网页解析器_4
            eg: https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggsDetail?guid=562df3b5-207a-4f2e-b3f7-3b29736ae191&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                text = etree.HTML(html)
                xpathPattern = "//div[@class='w1200s']//div[@class='page_contect bai_bg']//tr"
                node_list = text.xpath(xpathPattern)
                node = node_list[12]

                people_td = node.xpath('./td')[1]
                people = people_td.xpath('./p/span')[0].text

                price_td = node.xpath('./td')[2]
                price_tmp = price_td.xpath('./p/span')[0].text
                price = float(price_tmp)

                return people, price
            except:
                return None, 0.0

        def resolve_pp_5(html):
            '''
            子网页解析器_5
            eg: https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggsDetail?guid=61a3019b-33cb-44ba-a193-20c5d7f38543&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                text = etree.HTML(html)
                xpathPattern = "//div[@class='w1200s']//div[@class='page_contect bai_bg']//table"
                node_list = text.xpath(xpathPattern)
                tr_list = node_list[0].xpath('./tbody//tr')
                td_list = tr_list[1]
                people_td = td_list[2]
                people = people_td.xpath('./p/b/span')[0].text

                price_td = td_list[4]
                price_tmp = price_td.xpath('./p/b/span')[0].text
                price = float(price_tmp)

                return people, price
            except:
                return None, 0.0

        def resolve_pp_6(html):
            '''
            子网页解析器_6
            eg: https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggsDetail?guid=e8cc5564-4664-4d45-aabd-2690a3366e2b&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                text = etree.HTML(html)
                xpathPattern = "//div[@class='w1200s']//div[@class='page_contect bai_bg']//table//td[@colspan='4']//tr"
                node_list = text.xpath(xpathPattern)

                people = node_list[1].xpath('./td')[1].text

                price_tmp = node_list[1].xpath('./td')[4].text
                price = float(price_tmp)

                return people, price
            except:
                return None, 0.0

        def resolve_pp_7(html):
            '''
            子网页解析器_7
            eg: https://www.ynggzyxx.gov.cn/jyxx/jsgcZbjggsDetail?guid=2a7c021d-db9d-4dc5-8294-39083501dd9f&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                text = etree.HTML(html)
                xpathPattern = "//div[@class='w1200s']//div[@class='page_contect bai_bg']//table//tr"
                node_list = text.xpath(xpathPattern)
                people = node_list[9].xpath('./td')[1].xpath('./p/span')[0].text
                return people, 0.0
            except:
                return None, 0.0

        print("[+] 正在解析第{0}页信息".format(page_num))

        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        xpathPattern = "//div/table[@id='data_tab']/tbody/tr"
        node_list = text.xpath(xpathPattern)

        for node in node_list:
            if len(node.xpath("./td")) > 0:
                project_name = node.xpath("./td//a")[0].text
                project_name_parse = project_name.replace('\n', '').replace(u'\t', '').replace(u' ', '')
                startTime = node.xpath("./td")[2].text
                start_time = self.time_parse(startTime)

                href = "https://www.ynggzyxx.gov.cn" + node.xpath('./td//a//@href')[0]

                html_second = self.get_url(href, proxy_dict)

                people, price = resolve_pp_0(html_second)
                if people == '':
                    people, price = resolve_pp_2(html_second)

                if people == '':
                    people, price = resolve_pp_1(html_second)

                if people == '':
                    people, price = resolve_pp_3(html_second)

                if people == None:
                    people, price = resolve_pp_4(html_second)

                if people == None:
                    people, price = resolve_pp_5(html_second)

                if people == None:
                    people, price = resolve_pp_6(html_second)

                if people == None:
                    people, price = resolve_pp_7(html_second)

                # 存储到字典
                resolveMessage = {
                    "公告名称": project_name_parse,
                    "发布时间": start_time,
                    "链接": href,
                    "中标公司": people,
                    "中标价格": price,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)  # Done
    def resovler_ynsggzxxt_zf_zb(self, html, page_num):
        '''
        云南省公共资源交易信息网_政府采购_中标结果解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))

        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        xpathPattern = "//div/table[@id='data_tab']/tbody/tr"
        node_list = text.xpath(xpathPattern)

        for node in node_list:
            if len(node.xpath("./td")) > 0:
                project_name = node.xpath("./td//a")[0].text
                project_name_parse = project_name.replace('\n', '').replace(u'\t', '').replace(u' ', '')
                startTime = node.xpath("./td")[2].text
                start_time = self.time_parse(startTime)

                href = "https://www.ynggzyxx.gov.cn" + node.xpath('./td//a//@href')[0]

                # 存储到字典
                resolveMessage = {
                    "公告名称": project_name_parse,
                    "发布时间": start_time,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult


    @retry(tries=3, delay=2)  # Done
    def resovler_ynsggzzw_gc_zb(self, html, page_num, proxy_dict):
        '''
        云南省公共资源交易中心_工程建设_中标结果解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        def resolve_pp_1(html):
            '''
            子网页解析器_1
            eg: https://www.ynggzy.com/jyxx/jsgcZbjggsDetail?guid=fbd514af-5716-4e30-bc1d-b42892986f85&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                people = ''
                price = ''
                text = etree.HTML(html)
                node_second_list = text.xpath("//div[@class='con']//tr")
                for node_second in node_second_list:
                    if "中标人：" == node_second.xpath("./td")[0].text:
                        people = node_second.xpath("./td")[1].xpath('./b//span')[0].text
                    if "中标价" in node_second.xpath("./td")[0].text:
                        totalCount = node_second.xpath("./td")[1].xpath('./b//span')[0].text
                        price = totalCount
                return people, price
            except:
                return None, ''

        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []
        # 存储的列表
        text = etree.HTML(html)
        xpathPattern = "//div/table[@id='data_tab']/tbody/tr"
        node_list = text.xpath(xpathPattern)

        # 正则规约字段
        strParse = re.compile("\s")

        for node in node_list:
            if len(node.xpath("./td")) > 0:
                # 公告标题（正则规约）
                title = strParse.sub("", node.xpath("./td")[1].xpath("./a")[0].text)

                # 发布时间
                startTime = node.xpath("./td")[2].text
                start_time = self.time_parse(startTime)

                # href 链接地址
                href = "https://www.ynggzy.com" + str(node.xpath("./td/a/@href")[0])
                html_second = self.get_url(href, proxy_dict)
                people, price = resolve_pp_1(html_second)
                # 存储到字典
                resolveMessage = {
                    "公告标题": title,
                    "发布时间": start_time,
                    "链接": href,
                    "中标公司": people,
                    "中标价格": price,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)  # Done
    def resovler_ynsggzzw_zf_zb(self, html, page_num):
        '''
        云南省公共资源交易中心_政府采购_结果公示解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []
        # 存储的列表
        text = etree.HTML(html)
        xpathPattern = "//div/table[@id='data_tab']/tbody/tr"
        node_list = text.xpath(xpathPattern)

        # 正则规约字段
        strParse = re.compile("\s")

        for node in node_list:
            if len(node.xpath("./td")) > 0:
                # 公告标题（正则规约）
                title = strParse.sub("", node.xpath("./td")[1].xpath("./a")[0].text)

                # 发布时间
                startTime = node.xpath("./td")[2].text
                start_time = self.time_parse(startTime)

                # href 链接地址
                href = "https://www.ynggzy.com" + str(node.xpath("./td/a/@href")[0])
                # 存储到字典
                resolveMessage = {
                    "公告标题": title,
                    "发布时间": start_time,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult


    @retry(tries=3, delay=2)  # Done
    def resolver_kmsgg_gc_zb(self, html, page_num):
        '''
        昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        node_list = text.xpath("//div[@class='zb_from']/table/tbody/tr")
        for i in range(1, 16):
            # 编号
            num = node_list[i].xpath("./td")[1].text

            # 工程名称
            project_name = (node_list[i].xpath("./@field_bdmcggbt")[0]).encode('utf8')

            # 链接
            href = "https://www.kmggzy.com/Jyweb/" + str(node_list[i].xpath("./td/a/@href")[0])

            start_time = None
            # 发布时间
            startTime = node_list[i].xpath("./td")[3].text
            if startTime is not None:
                start_time = self.time_parse(startTime)

            # 存储到字典
            if num and project_name and start_time is not None:
                resolveMessage = {
                    "编号": num,
                    "工程名称": project_name,
                    "发布时间": start_time,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)  # Done
    def resolver_kmsgg_zf_zb(self, html, page_num):
        '''
        昆明市公共资源交易平台公共服务系统_政府采购_结果公示解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        node_list = text.xpath("//div[@class='zb_from']/table/tbody/tr")
        for i in range(1, 16):
            # 编号
            num = node_list[i].xpath("./td")[1].text

            # 工程名称
            project_name = (node_list[i].xpath("./@field_bdmcggbt")[0]).encode('utf8')

            # 链接
            href = "https://www.kmggzy.com/Jyweb/" + str(node_list[i].xpath("./td/a/@href")[0])

            start_time = None
            # 发布时间
            startTime = node_list[i].xpath("./td")[3].text
            if startTime is not None:
                start_time = self.time_parse(startTime)

            # 存储到字典
            if num and project_name and start_time is not None:
                resolveMessage = {
                    "编号": num,
                    "工程名称": project_name,
                    "发布时间": start_time,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)  # Done
    def resolver_kmsgg_gc_by(self, html, page_num):
        '''
        昆明市公共资源交易平台公共服务系统_工程建设_补遗通知解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        node_list = text.xpath("//div[@class='zb_from']/table/tbody/tr")
        for i in range(1, 16):
            # 编号
            num = node_list[i].xpath("./td")[1].text

            # 工程名称
            project_name = (node_list[i].xpath("./@field_bdmcggbt")[0]).encode('utf8')

            # 链接
            href = "https://www.kmggzy.com/Jyweb/" + str(node_list[i].xpath("./td/a/@href")[0])

            start_time = None
            # 发布时间
            startTime = node_list[i].xpath("./td")[3].text
            if startTime is not None:
                start_time = self.time_parse(startTime)

            # 存储到字典
            if num and project_name and start_time is not None:
                resolveMessage = {
                    "编号": num,
                    "工程名称": project_name,
                    "发布时间": start_time,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult

    @retry(tries=3, delay=2)  # Done
    def resolver_kmsgg_zf_by(self, html, page_num):
        '''
        昆明市公共资源交易平台公共服务系统_政府采购_补遗通知解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []

        # 解析源码并返回 XML 对象
        text = etree.HTML(html)

        node_list = text.xpath("//div[@class='zb_from']/table/tbody/tr")
        for i in range(1, 16):
            # 编号
            num = node_list[i].xpath("./td")[1].text

            # 工程名称
            project_name = (node_list[i].xpath("./@field_bdmcggbt")[0]).encode('utf8')

            # 链接
            href = "https://www.kmggzy.com/Jyweb/" + str(node_list[i].xpath("./td/a/@href")[0])

            start_time = None
            # 发布时间
            startTime = node_list[i].xpath("./td")[3].text
            if startTime is not None:
                start_time = self.time_parse(startTime)

            # 存储到字典
            if num and project_name and start_time is not None:
                resolveMessage = {
                    "编号": num,
                    "工程名称": project_name,
                    "发布时间": start_time,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult


    @retry(tries=3, delay=2)  # Done
    def resolver_ynszfcgw_cg(self, html, page_num, driver_second):
        '''
        云南省政府采购网_采购结果解析器
        :param html: 网页源码
        :param page_num: 网页页数
        :return: 返回包含数据字典的列表
        '''
        def resolver_pp_1(url_second):
            '''
            子网页解析器_1
            eg: https://www.ynggzy.com/jyxx/jsgcZbjggsDetail?guid=fbd514af-5716-4e30-bc1d-b42892986f85&isOther=false
            :param html:网页源码
            :return:中标公司和中标价格
            '''
            try:
                driver_second.get(url_second)
                people = driver_second.find_element_by_id('winSupply').get_attribute('value')
                price_tmp = driver_second.find_element_by_id('winMoney').get_attribute('value')
                price = price_tmp + "万元"
                return people, price
            except:
                return None, ''
        if page_num != 0:
            print("[+] 正在解析第{0}页信息".format(page_num))
        # 存储的列表
        resolveResult = []
        text = etree.HTML(html)
        for i in range(0, 10):
            node_list = text.xpath("//tr[@data-row-id='{0}']".format(i))

            for node in node_list:
                text_total = node.xpath('./td')[0].xpath('./a')[0].text

                # 编号
                num = text_total[:text_total.find('：')]

                # 工程名称
                project_name = text_total[text_total.find('：') + 1:]

                # 区划
                area = node.xpath('./td')[2].text

                time_push = None
                # 发布时间
                timePush = node.xpath('./td')[3].text
                if timePush is not None:
                    time_push = self.time_parse(timePush)

                # 链接
                cursor = node.xpath('./td')[0].xpath('./a/@data-bulletin_id')[0]

                href = "http://www.yngp.com/newbulletin_zz.do?method=preinsertgomodify&operator_state=1&flag=view&bulletin_id={0}".format(
                    cursor)

                people, price = resolver_pp_1(href)

                # 存储到字典
                resolveMessage = {
                    "编号": num,
                    "工程名称": project_name,
                    "区划": area,
                    "发布时间": time_push,
                    "中标公司": people,
                    "中标价格": price,
                    "链接": href,
                    "推送": False
                }
                resolveResult.append(resolveMessage)
        return resolveResult
