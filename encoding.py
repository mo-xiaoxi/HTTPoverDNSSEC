#!/usr/bin/env python
# -*- coding:utf-8 -*-
__Author__ = 'moxiaoxi'
"""
本文件主要完成各类编码工作
"""

import base64

BASE64U = 'base64u'

def encode(src,baseType = BASE64U):
    if baseType == BASE64U:
        return base64u_encode(src) #return True
    else:
        return False#非base64u类型的还没实现

def decode(src,baseType = BASE64U):
    if baseType == BASE64U:
        return base64u_decode(src) #return True
    else:
        return False

def base64u_encode(src):
    '''base64编码，=被舍去,+替换成_,/替换成-'''
    tmp = base64.b64encode(src)
    tmp = tmp.rstrip('=')
    tmp = tmp.replace('+','_')
    tmp = tmp.replace('/','-')
    return tmp
    

def base64u_decode(src):
    '''base64解码，=补上,_替换成+,-替换成/'''
    l = len(src)%4
    tmp = src+l*'='
    tmp = tmp.replace('_','+')
    tmp = tmp.replace('-','/')
    tmp = base64.b64decode(tmp)
    return tmp

def build_hostname(data,topdomain,maxlen=0xFF,baseType= BASE64U):
    space = maxlen - len(topdomain)-3-3 # 1 dot before topdomain 2 saftey 留两位(还一位是dot)用于进行count(面对网页过大情况下，需要多个dns请求才能拿到所有数据)
    buf = encode(data,baseType)
    l = len(buf)+len(buf)/64
    if l > space:
        raise 'url data is too long,please check it!'# 对于长度过长的url请求抛出异常，后期尝试从更好的方式处理这种异常
    buf = [buf[i:i+63] for i in range(0, len(buf), 63)]
    tmp = ''
    for i in buf:
        tmp +=(i+'.')
    count = 0x00
    while True:#迭代器生成hostname count使用16进制
        yield tmp+str(hex(count)[2:])+'.'+topdomain
        count +=1

def parse_hostname(data,topdomain,baseType = BASE64U):
    buf = data[:-len(topdomain)-1-1]#去除自定义域名的前缀和后缀dot
    buf = buf.split('.')
    tmp = ''
    index = int('0x'+buf[-1],16)
    for i in range(len(buf)-1):
        tmp +=buf[i]
    buf = decode(tmp,baseType)
    while True:
        yield buf,index

def parse_flag(flag):
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"
    return string.find(flag)

def build_flag(count):
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"
    return string[count]





