#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Author: YSW
Time: 2018-7-20
Version: 1.0
Describe: 控制台颜色打印控制
Update: None
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
'''
    开头部分：
        \033[显示方式;前景色;背景色m 

    结尾部分：
        \033[0m     

    完整格式： 
        <\033[显示方式;前景色;背景色m><要打印的文字><\033[0m> 
        如果有空格，空格也会打印出来
'''

# 显示方式参数
DISPLAY_TYPE = {
    "默认值": 0,
    "高亮": 1,
    "非粗体": 22,
    "下划线": 4,
    "非下划线": 24,
    "闪烁": 5,
    "非闪烁": 25,
    "反显": 7,
    "非反显": 27,
}

# 前景色参数
FOREGROUND_COLOR = {
    "黑色": 30,
    "红色": 31,
    "绿色": 32,
    "黄色": 33,
    "蓝色": 34,
    "洋红": 35,
    "青色": 36,
    "白色": 37,
}

# 背景色参数
BACKGROUND_COLOR = {
    "黑色": 40,
    "红色": 41,
    "绿色": 42,
    "黄色": 43,
    "蓝色": 44,
    "洋红": 45,
    "青色": 46,
    "白色": 47,
}

def _parameters_3(type, forecolor, backcolor):
    '''
    返回参数（3）
    :param type: 显示方式
    :param forecolor: 前景色
    :param backcolor: 背景色
    :return: 返回两个参数值
    '''
    display_type = DISPLAY_TYPE[type.encode('utf-8')]
    foreground_color = FOREGROUND_COLOR[forecolor.encode('utf-8')]
    back_color = BACKGROUND_COLOR[backcolor.encode('utf-8')]
    return display_type, foreground_color, back_color

def _parameters_2(type, forecolor):
    '''
    返回参数（2）
    :param type: 显示方式
    :param forecolor: 前景色
    :return: 返回两个参数值
    '''
    display_type = DISPLAY_TYPE[type.encode('utf-8')]
    foreground_color = FOREGROUND_COLOR[forecolor.encode('utf-8')]
    return display_type, foreground_color

def print_color_back(str, type, forecolor, backcolor):
    '''
    打印带背景色的字体
    :param str: 字符串
    :param type: 显示方式
    :param forecolor: 前景色
    :param backcolor: 背景色
    :return: 返回打印结果
    '''
    display_type, foreground_color, back_color = _parameters_3(type, forecolor, backcolor)
    head = "\033[{0};{1};{2}m".format(display_type, foreground_color, back_color)
    end = "\033[0m"
    str_color = head + str + end
    print(str_color)

def print_color(str, type="默认值", forecolor="绿色"):
    '''
    打印字体
    :param str: 字符串
    :param type: 显示方式
    :param forecolor: 前景色
    :return: 返回打印结果
    '''
    display_type, foreground_color = _parameters_2(type, forecolor)
    head = "\033[{0};{1}m".format(display_type, foreground_color)
    end = "\033[0m"
    str_color = head + str + end
    print(str_color)

def print_color_line(str, sign, step, type="默认值", forecolor="绿色"):
    '''
    打印带符号行的字体
    :param str: 字符串
    :param sign: 符号
    :param step: 步长
    :param type: 显示方式
    :param forecolor: 前景色
    :return: 返回打印结果
    '''
    display_type, foreground_color = _parameters_2(type, forecolor)
    head = "\033[{0};{1}m".format(display_type, foreground_color)
    end = "\033[0m"
    print(head)
    print(sign*int(step))
    print(str)
    print(sign*int(step))
    print(end)
