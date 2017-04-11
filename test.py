#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 压缩 加 多次请求
import requests
import binascii
from dnslib import DNSRecord
proxies = {
	"http":"http://127.0.0.1:7890",
	# "https":"https://127.0.0.1:7890"
}
res = requests.get("http://45.62.96.72/test2.html",proxies=proxies)
# res = requests.get("https://www.baidu.com",proxies=proxies)
# res = requests.get("http://45.62.96.72/test.html")
print res.content


# class DNSPacket(object):
# 	def __init__(self):
# 		self.reply = []

# 	def makeDNSreply(self):
# 		for i in range(10):
# 			self.reply.append(i)
# 		print self.reply

# class server(object):
# 	def __init__(self):
# 		self.DNS_Cache = {}

# 	def test(self):

# 		tmp = DNSPacket()
# 		tmp.makeDNSreply()
# 		print self.DNS_Cache
# 		self.DNS_Cache['hello']=tmp
# 		print self.DNS_Cache


# hhhh =server()
# hhhh.test()


import string
print string.printable