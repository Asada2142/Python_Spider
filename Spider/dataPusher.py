#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:05
# File    : dataPusher.py
# Version : 1.0
# Describe: 数据推送模块（旧版本推送方式）
# Update  :
'''

'''
    smtplib模块主要负责发送邮件：
        是一个发送邮件的动作，连接邮箱服务器，登录邮箱，发送邮件（有发件人，收信人，邮件内容）。
    
    email模块主要负责构造邮件：
        指的是邮箱页面显示的一些构造，如发件人，收件人，主题，正文，附件等。
    
    xlwt模块：
        操作excel
    
    pyExcelerator模块：
        操作excel，写入excel较为方便
    
'''
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders
from email.mime.base import MIMEBase
from email.utils import parseaddr, formataddr
import time
from pyExcelerator import *

class DataWrite(object):
    def __init__(self):
        print("[*] 正在初始化数据写入模块")
        self.excel_Workbook = Workbook()
        self.excel_Workbook_parse = Workbook()

    def excel_name(self, logic_file_type):
        '''
        获取当前时间，生成excel文件名
        文件名格式为：
            年月日_时分秒
            如：20180619_161819
        :return: excel文件名
        '''
        print("[+] 正在创建文件名称")
        current_time = time.strftime('%Y%m%d %H:%M:%S', time.localtime(time.time())).replace(' ', '_').replace(':', '')
        file_name = ""

        if logic_file_type == 0:
            file_name = r".\history_file\{0}.xls".format(current_time)
        elif logic_file_type == 1:
            file_name = r".\history_file\{0}[keyword].xls".format(current_time)
        elif logic_file_type == 2:
            file_name = r".\history_file\{0}_ZB.xls".format(current_time)
        elif logic_file_type == 3:
            file_name = r".\history_file\{0}_ZB[keyword].xls".format(current_time)

        print("[+] 创建成功")
        return file_name

    def excel_header(self, row, excel_sheet, excel_head_data, excel_sheet_name):
        '''
        生成excel标题头
        :param row: 当前标题的行数
        :param excel_sheet: 当前excel中的表
        :param excel_head_data: 标题列表数据
        :param excel_sheet_name: 表名
        :return:
        '''
        print("[*] 正在写入标题，表名：{0}".format(excel_sheet_name))
        try:
            index = 0
            for data in excel_head_data:
                excel_sheet.write(row, index, data)
                index += 1
            print("[+] 写入标题成功")
            return True
        except Exception, e:
            print("[-] 写入标题失败")
            print("ERROR: " + str(e.message))
            return False

    def excel_write(self, excel_sheet_name, excel_head_data, excel_data, logic_file_type):
        '''
        excel文件写入
        :param excel_sheet_name: excel的sheet表名
        :param excel_head_data: excel的标题列表数据
        :param excel_data: 要写入excel的数据
        :param logic_file_type: 判断文件是否为关键词提取文件
        :return: 返回生成的excel文件地址
        '''
        excel_name = self.excel_name(logic_file_type)
        try:
            print("[*] 正在写入文件")
            # 在excel文件中对应生成每一张表
            excel_sheet = self.excel_Workbook.add_sheet(excel_sheet_name)

            if self.excel_header(0, excel_sheet, excel_head_data, excel_sheet_name):
                index = 1
                for data in excel_data:
                    column_index = 0
                    for item in excel_head_data:
                        excel_sheet.write(index, column_index, data[item])
                        column_index += 1
                    index += 1
                self.excel_Workbook.save(excel_name)
            print("[+] 写入文件成功")
            return excel_name
        except Exception, e:
            print("[-] 写入文件失败")
            print("ERROR: " + str(e.message))
            return excel_name

    def excel_write_parse(self, excel_sheet_name, excel_head_data, excel_data, logic_file_type):
        '''
        excel文件写入（筛选后）
        :param excel_sheet_name: excel的sheet表名
        :param excel_head_data: excel的标题列表数据
        :param excel_data: 要写入excel的数据
        :param logic_file_type: 判断文件是否为关键词提取文件
        :return: 返回生成的excel文件地址
        '''
        excel_name = self.excel_name(logic_file_type)
        try:
            print("[*] 正在写入文件")
            # 在excel文件中对应生成每一张表
            excel_sheet = self.excel_Workbook_parse.add_sheet(excel_sheet_name)

            if self.excel_header(0, excel_sheet, excel_head_data, excel_sheet_name):
                index = 1
                for data in excel_data:
                    column_index = 0
                    for item in excel_head_data:
                        excel_sheet.write(index, column_index, data[item])
                        column_index += 1
                    index += 1
                self.excel_Workbook_parse.save(excel_name)
            print("[+] 写入文件成功")
            return excel_name
        except Exception, e:
            print("[-] 写入文件失败")
            print("ERROR: " + str(e.message))
            return excel_name

class DataSend(object):
    def __init__(self):
        print("[*] 正在初始化数据推送模块")

    def format_address(self, address):
        '''
        格式化邮件地址
        :param address: 邮件地址
        :return: 格式化后的邮件地址
        '''
        print("[+] 正在格式化邮件地址")
        name, addr = parseaddr(address)
        print("[+] 格式化完成")
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def send_mail(self, body, attachment):
        '''
        发送邮件
        :param body: 邮件正文
        :param attachment: 附件地址
        :return: 发送成功返回True
        '''
        print("[+] 开始发送邮件...")
        # 要发送的服务器
        smtp_server = 'smtp.qq.com'
        # 要发送的邮箱用户名/密码
        from_mail = '发送方邮箱地址'
        mail_pass = '邮箱SMTP服务密码'
        # 接收的邮箱
        to_mail = '接收方邮箱地址'

        # 构造一个 MIMEMultipart 对象代表邮件本身
        msg = MIMEMultipart()

        # Header 对中文进行转码
        msg['From'] = self.format_address('爬虫机器人 <%s>' % from_mail).encode()
        msg['To'] = to_mail
        msg['Subject'] = Header('今日份的招投标信息', 'utf-8').encode()

        # # plain 代表纯文本
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        # 二进制方式模式文件
        if len(attachment) != 0:
            for file_path in attachment:
                with open(file_path, 'rb') as excel:
                    # MIMEBase 表示附件的名字
                    mime = MIMEBase(file_path[str(file_path).rfind('\\') + 1: -4], 'xls',
                                    filename=file_path[str(file_path).rfind('\\') + 1:])

                    # filename 是显示附件名字
                    mime.add_header('Content-Disposition', 'attachment',
                                    filename=file_path[str(file_path).rfind('\\') + 1:])

                    # 获取附件内容
                    mime.set_payload(excel.read())
                    encoders.encode_base64(mime)

                    # 作为附件添加到邮件
                    msg.attach(mime)

        print("[+] 正在连接 SMTP 服务器")
        email = smtplib.SMTP_SSL(smtp_server, 465)
        print("[+] 连接成功")
        print("[+] 正在授权 SMTP 服务")
        login_code = email.login(from_mail, mail_pass)
        if login_code[0] is 235:
            print("[+] 授权成功")
        else:
            print("[-] 授权失败")
            return False
        try:
            # as_string()把 MIMEText 对象变成 str
            print("[+] 正在发送邮件")
            email.sendmail(from_mail, to_mail, msg.as_string())
            email.quit()
            print("[+] 发送成功")
            return True
        except Exception as e:
            print("[-] 发送失败")
            print("ERROR: " + str(e.message))
            return False
