#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/8/14 14:05
# File    : dataPusher_HTML.py
# Version : 1.0
# Describe: 数据推送模块（HTML版）
# Update  :
'''

import sys
import time
from Lib import Console_Color
import configManager
import dataDisposer
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

# 关键词列表
KEY_WORD = []
# 表的标题名
TABLE_TITLE = configManager.table_title
TENDER = dataDisposer.tenderDB

# 数据库
TENDER_TABLE = dataDisposer.DataOperate.dataOperate()

# 时间
DATE = dataDisposer.current_time()
TODAY_TIME = datetime.datetime(DATE.year, DATE.month, DATE.day, 0, 0, 0)


class HTML_Content(object):
    def __init__(self):
        Console_Color.print_color("[*] 正在初始化HTML数据写入模块")

    def get_data(self, table_name):
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
                # '推送': False
            })
        )
        tenderTable.update(
            {'推送': False},
            {'$set': {'推送': True}},
            multi=True,
            upsert=True
        )
        return list_data

    def delete_data(self, table_name):
        '''
        移除链接为空的数据行
        :param table_name: 数据表名称
        '''
        sheet = TENDER[table_name]
        sheet.remove({"链接": None})

    def current_time(self):
        time_parse = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return time_parse

    def html_name(self, logic_file_type):
        '''
        获取当前时间，生成 html 文件名
        文件名格式为：
        年月日_时分秒
        如：20180619_161819
        :return: html 文件名
        '''
        Console_Color.print_color("[+] 正在创建文件名称")
        current_time = time.strftime('%Y%m%d %H:%M:%S', time.localtime(time.time())).replace(' ', '_').replace(':', '')
        file_name = ""
        if logic_file_type == 0:
            file_name = r".\history_file\{0}.html".format(current_time)
        elif logic_file_type == 1:
            file_name = r".\history_file\{0}[keyword].html".format(current_time)
        elif logic_file_type == 2:
            file_name = r".\history_file\{0}_ZB.html".format(current_time)
        elif logic_file_type == 3:
            file_name = r".\history_file\{0}_ZB[keyword].html".format(current_time)
        Console_Color.print_color("[+] 创建成功")
        return file_name

    def __html_1(self, title, name):
        '''
        HTML网页第一部分
        :param title: 网页标题，如 “招投标信息”
        :param name: 当前网页名称，如 “今日份的招投标文件”
        :param desc: 描述信息
        :return: 返回网页第一部分信息
        '''
        desc = "推送时间：{0}".format(self.current_time())
        html1 = """
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>{0}</title></head><body bgcolor="white">
        </head>
        <body>
        <Center><H2>{1}</h2></Center>
        <p align="center">{2}</p>
        <Hr width="100%">
        <BR>
        """.format(title, name, desc)
        return html1

    def __html_content_header(self, current_website_name):
        '''
        分隔每个网站的标题头
        :param current_website_name: 标题名称
        :return: 带标题名称的网页信息
        '''
        Console_Color.print_color("[+] 创建网站标题头")
        html_header = """
        <hr width="100%" style="margin-top:-5px;border:3px solid blue;"/>
        <h3>{0}</h3>
        """.format(current_website_name)
        return html_header

    def __html_a(self, url, time_parse, name, dict_data):
        '''
        主要内容
        :param url: 子链接地址
        :param name: 标题
        :param time_parse: 时间
        :param *args: 其他内容
        :return: 返回主要内容
        '''
        Console_Color.print_color("[+] 写入主要内容: {0}".format(name))
        html_a = """
        <Hr width="100%">
        ├─<a>[{1}] #### </a><a href="{0}" target="_blank">{2}</a><br>
        """.format(url, time_parse, name)
        html_a_second = """"""
        for key, value in dict_data.items():
            html_a_second_tmp = """
            ├───────<a>{0}</a><br>
            """.format("{0}: {1}".format(key, value))
            html_a_second += html_a_second_tmp

        html = html_a + html_a_second + "<Hr width='100%'>"
        return html

    # Fixed
    def __html2(self):
        '''
        HTML网页第二部分
        :return: 返回网页第二部分信息
        '''
        html2 = """
        </body>
        </html>
        """
        return html2

    def html_content_func(self, list_data, current_website_name):
        '''
        网页主内容方法
        :param list_data: 数据列表
        :param current_website_name: 当前网站名称
        :return: 返回页面数据
        '''
        print("[*] 正在写入网页数据")
        html_content = self.__html_content_header(current_website_name)
        for data in list_data:
            url = str(data[u"链接"]).encode('utf-8')
            data.pop(u"链接")
            try:
                project_name = str(data[u"工程名称"]).encode('utf-8')
                data.pop(u"工程名称")
            except KeyError:
                try:
                    project_name = str(data[u"公告标题"]).encode('utf-8')
                    data.pop(u"公告标题")
                except KeyError:
                    project_name = str(data[u"公告名称"]).encode('utf-8')
                    data.pop(u"公告名称")

            time_parse = str(data[u"发布时间"]).encode('utf-8')
            data.pop(u"发布时间")
            data.pop(u"_id")
            data.pop(u"推送")
            html_content += self.__html_a(url, time_parse, project_name, data) + '\n'
        Console_Color.print_color("[+] 写入完成")
        return html_content

    def html_engine(self, title, name, html_content):
        '''
        HTML生成器
        :param title: 网页标题，如 “招投标信息”
        :param name: 当前网页名称，如 “今日份的招投标文件”
        :param current_website_name: 当前网站的标题名称，如 “云南省公共资源交易中心电子服务系统_工程建设”
        :param html_content: 当前网站的主要内容
        :return: 全网页
        '''
        Console_Color.print_color("[*] 正在生成HTML页面")
        html = \
                self.__html_1(title, name) \
                + "\n" \
                + html_content \
                + "\n" \
                + self.__html2()
        Console_Color.print_color("[+] 生成成功")
        return html

    def html_write(self, title, name, dict_html_data_name, logic_file_type):
        '''
        HTML 文件写入方法
        :param title: 网页标题
        :param name: 当前网页的名称
        :param func: 数据获取的方法
        :param list_html_data_name: 包含数据库表名和网站名称的字典
        :param logic_file_type: 文件标识
        :return html文件路径
        '''
        html_file_name = self.html_name(logic_file_type)
        html_con = """"""
        for table_name, table_value in dict_html_data_name.items():
            self.delete_data(table_name)
            current_website_name = table_value
            list_data = self.get_data(table_name)
            if list_data == []:
                continue
            html_content = self.html_content_func(list_data, current_website_name)
            html_con += html_content
        if html_con == """""":
            return ''
        html = self.html_engine(title, name, html_con)
        with open(html_file_name, "w") as f:
            f.write(html)
        return html_file_name

    def html_write_keywords(self, title, name, dict_html_data_name, logic_file_type):
        '''
        HTML 文件写入方法（加入关键词筛选）
        :param title: 网页标题
        :param name: 当前网页的名称
        :param func: 数据获取的方法
        :param list_html_data_name: 包含数据库表名和网站名称的字典
        :param logic_file_type: 文件标识
        :return html文件路径
        '''
        html_file_name = self.html_name(logic_file_type)
        html_con = """"""
        for table_name, table_value in dict_html_data_name.items():
            self.delete_data(table_name)
            current_website_name = table_value
            list_data = self.get_data(table_name)
            # 读取关键词文件并生成关键字列表
            with open(r".\keyword_file\keyword.txt", 'r') as f:
                line = f.read()
                if line not in KEY_WORD:
                    KEY_WORD.append(line)
            key_word = str(KEY_WORD[0]).split('\n')

            # 筛选关键词信息
            list_data_parse = []
            for data in list_data:
                for key in key_word:
                    # 获取每张表对应的标题字段并判断是否包含关键词信息
                    if key in data[TABLE_TITLE[table_name]] and data not in list_data_parse:
                        list_data_parse.append(data)
            if list_data_parse == []:
                continue
            html_content = self.html_content_func(list_data_parse, current_website_name)
            html_con += html_content
        if html_con == """""":
            return ''
        html = self.html_engine(title, name, html_con)
        with open(html_file_name, "w") as f:
            f.write(html)
        return html_file_name
