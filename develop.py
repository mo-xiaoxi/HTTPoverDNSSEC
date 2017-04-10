#!/usr/bin/env python
# -*- coding:utf-8 -*-

import base64
import string
import dns.resolver

BUFSIZE = 512

def encode(content):
	tmp = base64.b64encode(content)
	print 'base64:',tmp
	tmp = tmp.rstrip('=')
	tmp = tmp.replace('+','_')
	tmp = tmp.replace('/','-')
	return tmp

def decode(recv):
	'''base64解码，=被舍去,+替换成_'''
	l = len(recv)%4
	tmp = recv+l*'='
	tmp = tmp.replace('_','+')
	tmp = tmp.replace('-','/')
	print tmp
	tmp = base64.b64decode(tmp)
	return tmp


def build_hostname(data,topdomain,maxlen=0xFF):
	space = maxlen - len(topdomain)-3 # 1 dot before topdomain 2 saftey
	print data
	buf = encode(data)
	print 'encode data:',buf,len(buf)
	l = len(buf)+len(buf)/64
	if l > space:
		print 'data is too long!'
		return False
	buf = [buf[i:i+63] for i in range(0, len(buf), 63)]
	tmp = ''
	for i in buf:
		tmp +=(i+'.')
	buf = tmp + topdomain
	return buf

def parse_hostname(data,topdomain):
	buf = data[:-len(topdomain)-1]
	buf = buf.split('.')
	tmp = ''
	for i in buf:
		tmp +=i
	print tmp,len(tmp)
	return decode(tmp)

buff = 'reverse()直接就把数组逆序了,只需要输出的话就这样好了: a =[1,2,3,4,5,6] ... 2008-08-05 10:48. python 新'
topdomain = 'xiaoxi.wanmitech.com'
hostname = build_hostname(buff,topdomain)
print hostname
parse_hostname(hostname,topdomain)
# A = dns.resolver.query('baidu.com','TXT')
# test = dns.resolver.query(hostname,'TXT')

print decode(encode('test'))




