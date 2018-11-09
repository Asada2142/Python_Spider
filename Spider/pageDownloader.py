#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:03
# File    : pageDownloader.py
# Version : 2.0
# Describe: 网页下载器
# Update  :
        1.重构了网页下载器，只存储当天的数据
        2.优化了排序算法
'''

from selenium import webdriver
# 引入配置对象DesiredCapabilities
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import configManager
import random
import sys
import socket
import time
import pageResolver
import dataDisposer
import urllib2
from Lib import Console_Color

# 设置默认编码，防止出现中文字符乱码
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
HEADERS = {
    "User-Agent": random.choice(configManager.headers)
}

URL = configManager.urlData
URL_ZB = configManager.urlData_ZB

class DownLoader(object):
    def __init__(self, headers):
        self.headers = headers
        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
        self.dcap["phantomjs.page.settings.userAgent"] = self.headers
        # 不载入图片，爬页面速度会快很多
        self.dcap["phantomjs.page.settings.loadImages"] = False

    @staticmethod
    def get_url(url, proxy_dict):
        '''
        获得静态页面
        :param url: 静态页面 URL 地址
        :param proxy_dict: 代理
        :return: 返回静态网页源代码
        '''
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

    def current_time_parse(self, current_date):
        '''
        获取当前时间，返回月份和天数
        :return: 当前月份和天数
        '''
        current_month = current_date.month
        current_day = current_date.day
        return current_month, current_day

    def check_exist(self, tender_table, condition1, value1, condition2, value2):
        '''
        判断数据是否存在
        :param tender_table: 数据表
        :param condition1: 条件1
        :param value1: 条件值1
        :param condition2: 条件2
        :param value2: 条件值2
        :return: 不为空返回 False, 为空返回 True
        '''
        list_data = list(tender_table.find(
                {
                    condition1: value1,
                    condition2: value2
                }
            )
        )
        if len(list_data) == 0:
                return True
        return False

    #### 招投标数据 ####

    def downloader_ynsggzxxt(self, url, proxy_dict):
        '''
        云南省公共资源交易中心电子服务系统下载器
        '''
        website_name = "云南省公共资源交易中心电子服务系统_工程建设"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynsggzxxt')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 201):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resovler_ynsggzxxt(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception
                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_class_name("mmggxlh").find_element_by_link_text('下一页').click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()
        for resolve in data_list:
            projectNumber = resolve["项目编号"]
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            end_time = resolve["截止时间"]
            status = resolve["状态"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 项目编号：{0}，公告标题：{1}，发布时间：{2}，截止时间：{3}，状态：{4}，链接：{5}".format(projectNumber, title.encode('utf-8'),
                                                                                 start_time, end_time,
                                                                                 status.encode('utf-8'), href))

        for resolve in data_list:
            # 打印
            projectNumber = resolve["项目编号"]
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            end_time = resolve["截止时间"]
            status = resolve["状态"]
            href = resolve["链接"]
            if self.check_exist(tender_table, condition1="项目编号", value1=projectNumber, condition2="公告标题", value2=title):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 项目编号：{0}，公告标题：{1}，发布时间：{2}，截止时间：{3}，状态：{4}，链接：{5}".format(projectNumber, title.encode('utf-8'), start_time, end_time, status.encode('utf-8'), href))
                print("[+] 存储成功")

    def downloader_ynsggzxxt_zf(self, url, proxy_dict):
        '''
        云南省公共资源交易中心电子服务系统下载器
        '''
        website_name = "云南省公共资源交易中心电子服务系统_政府采购"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynsggzxxt_zf')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 201):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resovler_ynsggzxxt_zf(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_class_name("mmggxlh").find_element_by_link_text('下一页').click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["项目编号"]
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            end_time = resolve["截止时间"]
            status = resolve["状态"]
            href = resolve["链接"]
            Console_Color.print_color(
                "[+] 项目编号：{0}，公告标题：{1}，发布时间：{2}，截止时间：{3}，状态：{4}，链接：{5}".format(projectNumber, title.encode('utf-8'),
                                                                               start_time, end_time,
                                                                               status.encode('utf-8'), href))

        for resolve in data_list:
            # 打印
            projectNumber = resolve["项目编号"]
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            end_time = resolve["截止时间"]
            status = resolve["状态"]
            href = resolve["链接"]
            if self.check_exist(tender_table, condition1="项目编号", value1=projectNumber, condition2="公告标题", value2=title):
                # 存储信息
                dataSaver.insert_data(resolve)
                print(
                    "[+] 项目编号：{0}，公告标题：{1}，发布时间：{2}，截止时间：{3}，状态：{4}，链接：{5}".format(projectNumber, title.encode('utf-8'),
                                                                                   start_time, end_time,
                                                                                   status.encode('utf-8'), href))
                print("[+] 存储成功")

    def downloader_ynsggzzw(self, url, proxy_dict):
        '''
        云南省公共资源交易中心网（旧）下载器
        '''
        website_name = "云南省公共资源交易中心网_工程建设"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynsggzzw')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 101):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            resolve_result = resolver.resovler_ynsggzzw(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception
                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_class_name("mmggxlh").find_element_by_link_text('下一页').click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["项目编号"]
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 项目编号：{0}，公告标题：{1}，发布时间：{2}，链接：{3}".format(projectNumber, title.encode('utf-8'), start_time,
                                                                 href))

        for resolve in data_list:
            # 打印
            projectNumber = resolve["项目编号"]
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            if self.check_exist(tender_table, condition1="项目编号", value1=projectNumber, condition2="公告标题", value2=title):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 项目编号：{0}，公告标题：{1}，发布时间：{2}，链接：{3}".format(projectNumber, title.encode('utf-8'), start_time,
                                                                     href))
                print("[+] 存储成功")

    def downloader_kmsgg(self, url, proxy_dict):
        '''
        昆明市公共资源交易中心网下载器
        '''
        website_name = "昆明市公共资源交易中心网_政府采购"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('kmsgg')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 51):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resovler_kmsgg(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_id("btnAjax_NextPage").click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            end_time = resolve["结束时间"]
            status = resolve["状态"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，结束时间：{3}，状态：{4}，链接：{5}".format(projectNumber, project_name,
                                                                               start_time, end_time, status, href))


        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            end_time = resolve["结束时间"]
            status = resolve["状态"]
            href = resolve["链接"]

            if self.check_exist(tender_table, condition1="编号", value1=projectNumber, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，结束时间：{3}，状态：{4}，链接：{5}".format(projectNumber, project_name,
                                                                                   start_time, end_time, status, href))
                print("[+] 存储成功")

    def downloader_kmsgg_gc(self, url, proxy_dict):
        '''
        昆明市公共资源交易中心网下载器
        '''
        website_name = "昆明市公共资源交易中心网_工程建设"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('kmsgg_gc')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 51):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resovler_kmsgg_gc(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_id("btnAjax_NextPage").click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            end_time = resolve["结束时间"]
            status = resolve["状态"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，结束时间：{3}，状态：{4}，链接：{5}".format(projectNumber, project_name,
                                                                               start_time, end_time, status, href))

        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            end_time = resolve["结束时间"]
            status = resolve["状态"]
            href = resolve["链接"]

            if self.check_exist(tender_table, condition1="编号", value1=projectNumber, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，结束时间：{3}，状态：{4}，链接：{5}".format(projectNumber, project_name,
                                                                                   start_time, end_time, status, href))
                print("[+] 存储成功")

    def downloader_ynszfcgw(self, url, proxy_dict):
        '''
        云南省政府采购网下载器
        '''
        website_name = "云南省政府采购网"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        # 不知道为什么 PhantomJS 打不开这个网站
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynszfcgw')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 201):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resovler_ynszfcgw(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_xpath('//a[@data-page="next"]').click()
            except Exception:
                break

            # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()
        for resolve in data_list:
            # 打印
            area = resolve["区划"]
            project_number = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 区划：{0}，编号：{1}，工程名称：{2}，发布时间：{3}，链接：{4}".format(area.encode('utf-8'),
                                                                      project_number.encode('utf-8'),
                                                                      project_name.encode('utf-8'), start_time,
                                                                      href))

        for resolve in data_list:
            # 打印
            area = resolve["区划"]
            project_number = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]

            if self.check_exist(tender_table, condition1="编号", value1=project_number, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 区划：{0}，编号：{1}，工程名称：{2}，发布时间：{3}，链接：{4}".format(area.encode('utf-8'),
                                                                          project_number.encode('utf-8'),
                                                                          project_name.encode('utf-8'), start_time,
                                                                          href))
                print("[+] 存储成功")


    #### 中标数据 ####
    def downloader_ynsggzxxt_gc_zb(self, url, proxy_dict):
        '''
        云南省公共资源交易信息网_工程建设_中标公告下载器
        '''
        website_name = "云南省公共资源交易信息网_工程建设_中标公告"
        print(url)
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynsggzxxt_gc_zb')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 201):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resovler_ynsggzxxt_gc_zb(html, page_num, proxy_dict)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception
                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_class_name("mmggxlh").find_element_by_link_text('下一页').click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            project_name_parse = resolve["公告名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            people = resolve["中标公司"]
            price = resolve["中标价格"]
            Console_Color.print_color("[+] 项目名称：{0}，发布时间：{1}，链接：{2}，中标人：{3}，中标价：{4}".format(project_name_parse.encode('utf-8'), start_time, href.encode('utf-8'), people, price))

        for resolve in data_list:
            # 打印
            project_name_parse = resolve["公告名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            people = resolve["中标公司"]
            price = resolve["中标价格"]
            if self.check_exist(tender_table, condition1="链接", value1=href, condition2="公告名称", value2=project_name_parse):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 项目名称：{0}，发布时间：{1}，链接：{2}，中标人：{3}，中标价：{4}".format(project_name_parse.encode('utf-8'), start_time, href.encode('utf-8'), people, price))
                print("[+] 存储成功")

    def downloader_ynsggzxxt_zf_zb(self, url, proxy_dict):
        '''
        云南省公共资源交易信息网_政府采购_中标结果下载器
        '''
        website_name = "云南省公共资源交易信息网_政府采购_中标结果"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynsggzxxt_zf_zb')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 201):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resovler_ynsggzxxt_zf_zb(html, page_num)
            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception
                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_class_name("mmggxlh").find_element_by_link_text('下一页').click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            project_name_parse = resolve["公告名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 项目名称：{0}，发布时间：{1}，链接：{2}".format(project_name_parse.encode('utf-8'), start_time, href.encode('utf-8')))

        for resolve in data_list:
            # 打印
            project_name_parse = resolve["公告名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            if self.check_exist(tender_table, condition1="链接", value1=href, condition2="公告名称", value2=project_name_parse):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 项目名称：{0}，发布时间：{1}，链接：{2}".format(project_name_parse.encode('utf-8'), start_time, href.encode('utf-8')))
                print("[+] 存储成功")


    def downloader_ynsggzzw_gc_zb(self, url, proxy_dict):
        '''
        云南省公共资源交易中心_工程建设_中标结果下载器
        '''
        website_name = "云南省公共资源交易中心_工程建设_中标结果"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynsggzzw_gc_zb')
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 101):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            resolve_result = resolver.resovler_ynsggzzw_gc_zb(html, page_num, proxy_dict)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception
                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_class_name("mmggxlh").find_element_by_link_text('下一页').click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            title = resolve["公告标题"]
            people = resolve["中标公司"]
            price = resolve["中标价格"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 公告标题：{0}，发布时间：{1}，中标人：{2}，中标价：{3}，链接：{4}".format(title.encode('utf-8'), start_time,
                                                                    people.encode('utf-8'), price.encode('utf-8'),
                                                                    href))

        for resolve in data_list:
            # 打印
            title = resolve["公告标题"]
            people = resolve["中标公司"]
            price = resolve["中标价格"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            if self.check_exist(tender_table, condition1="链接", value1=href, condition2="公告标题", value2=title):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 公告标题：{0}，发布时间：{1}，中标人：{2}，中标价：{3}，链接：{4}".format(title.encode('utf-8'), start_time,
                                                                    people.encode('utf-8'), price.encode('utf-8'),
                                                                    href))
                print("[+] 存储成功")

    def downloader_ynsggzzw_zf_zb(self, url, proxy_dict):
        '''
        云南省公共资源交易中心_政府采购_结果公示下载器
        '''
        website_name = "云南省公共资源交易中心_政府采购_结果公示"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynsggzzw_zf_zb')
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 101):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            resolve_result = resolver.resovler_ynsggzzw_zf_zb(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception
                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_class_name("mmggxlh").find_element_by_link_text('下一页').click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 公告标题：{0}，发布时间：{1}，链接：{2}".format(title.encode('utf-8'), start_time, href))

        for resolve in data_list:
            # 打印
            title = resolve["公告标题"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            if self.check_exist(tender_table, condition1="链接", value1=href, condition2="公告标题", value2=title):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 公告标题：{0}，发布时间：{1}，链接：{2}".format(title.encode('utf-8'), start_time, href))
                print("[+] 存储成功")


    def downloader_kmsgg_gc_zb(self, url, proxy_dict):
        '''
        昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示下载器
        '''
        website_name = "昆明市公共资源交易平台公共服务系统_工程建设_中标结果公示"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('kmsgg_gc_zb')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 51):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resolver_kmsgg_gc_zb(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_id("btnAjax_NextPage").click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                               start_time, href))


        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]

            if self.check_exist(tender_table, condition1="编号", value1=projectNumber, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                                   start_time, href))
                print("[+] 存储成功")

    def downloader_kmsgg_zf_zb(self, url, proxy_dict):
        '''
        昆明市公共资源交易平台公共服务系统_政府采购_结果公示下载器
        '''
        website_name = "昆明市公共资源交易平台公共服务系统_政府采购_结果公示"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('kmsgg_zf_zb')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 51):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resolver_kmsgg_zf_zb(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_id("btnAjax_NextPage").click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                               start_time, href))


        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]

            if self.check_exist(tender_table, condition1="编号", value1=projectNumber, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                                   start_time, href))
                print("[+] 存储成功")

    def downloader_kmsgg_gc_by(self, url, proxy_dict):
        '''
        昆明市公共资源交易平台公共服务系统_工程建设_补遗通知下载器
        '''
        website_name = "昆明市公共资源交易平台公共服务系统_工程建设_补遗通知"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('kmsgg_gc_by')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 51):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resolver_kmsgg_gc_by(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_id("btnAjax_NextPage").click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                               start_time, href))


        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]

            if self.check_exist(tender_table, condition1="编号", value1=projectNumber, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                                   start_time, href))
                print("[+] 存储成功")

    def downloader_kmsgg_zf_by(self, url, proxy_dict):
        '''
        昆明市公共资源交易平台公共服务系统_政府采购_补遗通知下载器
        '''
        website_name = "昆明市公共资源交易平台公共服务系统_政府采购_补遗通知"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('kmsgg_zf_by')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(1, 51):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resolver_kmsgg_zf_by(html, page_num)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_id("btnAjax_NextPage").click()
            except Exception:
                break

        # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()

        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            Console_Color.print_color("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                               start_time, href))


        for resolve in data_list:
            # 打印
            projectNumber = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]

            if self.check_exist(tender_table, condition1="编号", value1=projectNumber, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 编号：{0}，工程名称：{1}，发布时间：{2}，链接：{3}".format(projectNumber, project_name,
                                                                                   start_time, href))
                print("[+] 存储成功")


    def downloader_ynszfcgw_cg(self, url, proxy_dict):
        '''
        云南省政府采购网_采购结果下载器
        '''
        website_name = "云南省政府采购网_采购结果"
        Console_Color.print_color("[+] 当前网站：{0}".format(website_name), forecolor="青色")
        # 设置代理
        proxyIP = proxy_dict['ip']
        proxyPort = proxy_dict['port']
        proxyProtocol = proxy_dict['protocol']
        service_args = ['--proxy={0}:{1}', '--proxy-type={2}'.format(proxyIP, proxyPort, proxyProtocol)]
        # 初始化driver对象，传入浏览器报头参数和代理IP，并获取网页URL
        # 不知道为什么 PhantomJS 打不开这个网站
        driver = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver_second = webdriver.PhantomJS(desired_capabilities=self.dcap, service_args=service_args)
        driver.get(url)

        # 点击后加载到中标页面
        driver.find_element_by_class_name("panel-heading-search").find_element_by_link_text('中标、成交公告').click()

        # 创建网页解析器对象
        resolver = pageResolver.Resolver()

        # 创建数据存储对象
        dataSaver = dataDisposer.DataStore('ynszfcgw_cg')
        # 创建表对象
        tender_table = dataSaver.tender_table()

        # 获取当前时间
        current_date = dataDisposer.current_time()

        data_list = []

        print("[*] 开始存储数据")
        for page_num in range(0, 201):
            # 设置时间戳，防止被识别
            timeout = 20
            socket.setdefaulttimeout(timeout)
            sleep_download_time = 3
            time.sleep(sleep_download_time)

            print("[+] 正在抓取第{0}页信息".format(page_num))
            html = driver.page_source
            print("[+] 抓取成功")

            # 解析网页
            resolve_result = resolver.resolver_ynszfcgw_cg(html, page_num, driver_second)

            # 获取当前的月数和天数
            current_month, current_day = self.current_time_parse(current_date)
            # 如果加载到最后一页就停止点击
            try:
                for resolve in sorted(resolve_result, key=lambda x: x['发布时间'], reverse=True):
                    # 获取发布时间的月数和天数
                    resolve_month, resolve_day = self.current_time_parse(resolve['发布时间'])
                    # 如果是当天时间的数据，则进行存储
                    if int(current_month) == int(resolve_month):
                        if int(current_day) == int(resolve_day):
                            data_list.append(resolve)
                        else:
                            print("[+] 获取完成")
                            raise Exception
                    else:
                        print("[+] 获取完成")
                        raise Exception

                # 模拟点击网页的下一页，获取动态加载的全部网页
                driver.find_element_by_xpath('//a[@data-page="next"]').click()
            except Exception:
                break

            # 关闭当前页面，如果只有一个页面
        driver.close()

        # 关闭浏览器
        driver.quit()
        for resolve in data_list:
            # 打印
            area = resolve["区划"]
            project_number = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            people = resolve["中标公司"]
            price = resolve["中标价格"]
            Console_Color.print_color("[+] 区划：{0}，编号：{1}，工程名称：{2}，发布时间：{3}，链接：{4}，中标公司：{5}，中标价格：{6}".format(
                                                                                        area.encode('utf-8'),
                                                                                        project_number.encode('utf-8'),
                                                                                        project_name.encode('utf-8'),
                                                                                        start_time,
                                                                                        href,
                                                                                        people.encode('utf-8'),
                                                                                        price.encode('utf-8')
                                                                                        ))

        for resolve in data_list:
            # 打印
            area = resolve["区划"]
            project_number = resolve["编号"]
            project_name = resolve["工程名称"]
            start_time = resolve["发布时间"]
            href = resolve["链接"]
            people = resolve["中标公司"]
            price = resolve["中标价格"]

            if self.check_exist(tender_table, condition1="编号", value1=project_number, condition2="工程名称",
                                value2=project_name):
                # 存储信息
                dataSaver.insert_data(resolve)
                print("[+] 区划：{0}，编号：{1}，工程名称：{2}，发布时间：{3}，链接：{4}，中标公司：{5}，中标价格：{6}".format(area.encode('utf-8'),
                                                                          project_number.encode('utf-8'),
                                                                          project_name.encode('utf-8'), start_time,
                                                                          href,
                                                                          people.encode('utf-8'),
                                                                          price.encode('utf-8')))
                print("[+] 存储成功")
