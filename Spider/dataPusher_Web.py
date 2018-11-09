#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:05
# File    : dataPusher.py
# Version : 1.0
# Describe: 数据推送模块（测试版）
# Update  :
'''

class DataPusher_Web(object):
    def __init__(self):
        pass

    def html_1(self, title, name, desc):
        html1 = """
            <html><head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <title>{0}</title></head><body bgcolor="white">
            <Center><H2>{1}</h2></Center>
            <p align="center">{2}</p>
            <Hr width="100%"><BR>
            """.format(title, name, desc)
        return html1

    def html_a(self, url, time_sort, project_name):
        html_a = """
        ├─<a href="{0}" target="_blank">{1}: {2}</a><br>
        """.format(url, time_sort, project_name)
        return html_a

    def html_2(self):
        html2 = """
            </body>
            </html>
            """
        return html2

    def html_maker(self, list_data):
        html_content = """"""
        for data in list_data:
            url = str(data[u"链接"]).encode('utf-8')
            time_parse = str(data[u"发布时间"]).encode('utf-8')
            project_name = str(data[u"公告标题"]).encode('utf-8')
            html_content += self.html_a(url, time_parse, project_name) + '\n'
        return html_content

    def html_writer(self, file_name, title, name, desc, list_data):
        html_content = self.html_maker(list_data)
        html_part1 = self.html_1(title, name, desc)
        html_part2 = self.html_2()
        html = html_part1 + "\n" + html_content + "\n" + html_part2
        htmlEncode = html.encode('utf-8')
        with open(u"C:\\Users\\Administrator\\Desktop\\{0}.html".format(file_name), "w") as f:
            f.write(htmlEncode)





