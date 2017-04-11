#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import binascii
from dnslib import DNSRecord
proxies = {
	"http":"http://127.0.0.1:7899",
	# "https":"https://127.0.0.1:7890"
}
res = requests.get("http://momomoxiaoxi.com",proxies=proxies)
# res = requests.get("https://www.baidu.com",proxies=proxies)
# res = requests.get("http://45.62.96.72/test2.html")
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


class DNSPacket(object):
	def __init__(self,request,response,TTL=100,DNSsize=255,UDPsize=1472):
		self.id = request.header.id
		self.q = request.q
		self.rname = request.q.qname
		self.TTL = TTL
		self.response = response
		self.length = len(response)
		self.offset = 0
		self.DNSsize = DNSsize
		self.UDPsize = UDPsize
		self.reply = []

	def makeDNSreply(self):
		response = self.response+END_FLAG
		l = len(response)
		base = self.UDPsize/self.DNSsize
		DNScount = l/self.DNSsize + 1
		UDPcount = DNScount/base+1
		i = 0
		for j in range(1,UDPcount+1):
			tmp_reply = DNSRecord(DNSHeader(id=self.id , qr=1, aa=1, ra=1), q=self.q)
			while i < base*j:
				if(self.DNSsize*i>l):
					break
				packet = response[self.DNSsize*i:self.DNSsize*(i+1)]
				logging.debug("packet:{0},i:{1},j:{2}".format(packet,i,j))
				tmp_reply.add_answer(RR(rname=self.rname, rtype=QTYPE.TXT, rclass=1, ttl=self.TTL, rdata=TXT(packet)))
				i += 1
			self.reply.append(tmp_reply.pack())
		print 'len self reply',len(self.reply)