#!/usr/bin/env Python
# -*- coding: utf-8 -*-
'''
# Author  : YSW
# Time    : 2018/6/6 14:04
# File    : dataDisposer.py
# Version : 1.0
# Describe: 数据处理器
# Update  :
        1.数据更新
        2.数据清洗
'''

import pymongo
import datetime
import time
import configManager
import sys
# 设置默认编码，防止出现中文字符乱码
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

# 获取数据库配置文件
__dbParam = configManager.dataBaseParams
# 连接 mongodb
__client = pymongo.MongoClient(__dbParam["userName"], __dbParam["port"])
# 创建数据库
tenderDB = __client[__dbParam["dataBaseName"]]
# 创建数据库
logDB = __client[__dbParam["logBaseName"]]

def current_time():
    '''
    获取当前时间
    :return: 返回格式化后的时间数据
    '''
    print("[*] 正在获取当前时间")
    currentTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    date = datetime.datetime.strptime(currentTime, '%Y-%m-%d %H:%M:%S')
    print("[+] 获取完成")
    return date

class DataOperate(object):
    '''
    单独的数据库类，返回数据表库对象
    '''
    @staticmethod
    def dataOperate():
        return tenderDB

    @staticmethod
    def logOperate():
        return logDB
		
class DataStore(object):
    '''
    数据库操作类
    '''
    def __init__(self, tenderDBName):
        print("[*] 正在初始化数据库操作模块")
        # 创建数据表，用于存储招标信息
        self.__tenderTable = tenderDB[tenderDBName]

    def tender_table(self):
        '''
        数据表
        :return: 返回数据表
        '''
        return self.__tenderTable

    def insert_data(self, dict_data):
        '''
        数据插入
        :param dict_data: 数据字典
        '''
        self.__tenderTable.insert_one(dict_data)

    def delete_data(self, dict_data):
        '''
        数据删除
        :param dict_data: 数据字典
        '''
        self.__tenderTable.delete_one(dict_data)

    def delete_none_data(self):
        '''
        删除链接或特定字符为 None 的数据
        '''
        self.__tenderTable.delete_many({"链接": None})

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
            map_id = map(lambda doc: doc['dups'][1:], self.__tenderTable.aggregate(pipeline=pipeline))
            list_id = [item for sublist in map_id for item in sublist]
            list(map(lambda _id: self.delete_data({'_id': _id}), list_id))
            print("[+] 数据清洗完成")
        except Exception, e:
            print("[-] 数据清洗失败")
            print("ERROR: " + str(e.message))

    def update_date_by_time(self, update_filed):
        '''
        数据更新
        当前时间小于或者等于截止时间时
        状态字段就更新为已截止
        :param: 需要进行更新的字段
        :return:
        '''
        print("[+] 开始进行数据更新")
        currentDateTime = current_time()
        try:
            self.__tenderTable.update(
                {update_filed: {"$lte": currentDateTime}},
                {'$set': {'状态': '已截止'}},
                multi=True,
                upsert=True
            )
            print("[+] 数据更新完成")
        except Exception, e:
            print("[-] 数据更新失败")
            print("ERRRO: " + str(e.message))
