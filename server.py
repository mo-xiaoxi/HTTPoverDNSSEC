#!/usr/bin/env python
# encoding: utf-8

import socket
import logging
import threading
import requests
import base64
from dnslib import DNSRecord,QTYPE,DNSHeader,RR,TXT
from  encoding import *

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s',
)

LUDP_ADDR = ('0.0.0.0',53)
TIMEOUT = 20
MAX_RESEND_COUNT = 10
END_FLAG = 'DNSEND'
BUFSIZE = 255
DNSBUF = 1024

class DNSPacket(object):
	def __init__(self,response,TTL=100,DNSsize=255,UDPsize=1472):
		self.TTL = TTL
		self.response = response
		self.length = len(response)
		self.offset = 0
		self.DNSsize = DNSsize
		self.UDPsize = UDPsize
		self.UDPpacket = []

	def GetDNSreply(self,request,index):
		if (index >= len(self.UDPpacket)):
			index = len(self.UDPpacket)-1 #防止最后一个数据包丢失导致的越界问题
		reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
		for i in range(len(self.UDPpacket[index])):
			packet = self.UDPpacket[index][i]
			reply.add_answer(RR(rname=request.q.qname, rtype=QTYPE.TXT, rclass=1, ttl=self.TTL, rdata=TXT(packet)))
		return reply.pack()

	def makereply(self):
		response = self.response+END_FLAG
		l = len(response)
		base = self.UDPsize/self.DNSsize
		DNScount = l/self.DNSsize + 1
		UDPcount = DNScount/base+1
		i = 0
		for j in range(1,UDPcount+1):
			oneUDPpacket = []
			while i < base*j:
				if(self.DNSsize*i>l):
					break
				DNSpacket = response[self.DNSsize*i:self.DNSsize*(i+1)]
				oneUDPpacket.append(DNSpacket)
				i += 1
			self.UDPpacket.append(oneUDPpacket)
		print len(self.UDPpacket)
# 	def send


class Server(object):
	def __init__(self,ludp_addr,topdomain):
		self.ludp_addr = ludp_addr
		self.running = True
		self.timeout = TIMEOUT
		self.topdomain = topdomain
		self.httpheader = ''
		self.DNS_Cache = {}

	def main_loop(self):
		try:
			self.dns_server = self.start_dns_server()
			while True:
				http_proxy_thread = threading.Thread(target=self.handler,args=self.dns_server.recvfrom(DNSBUF))
				http_proxy_thread.daemon = True
				http_proxy_thread.start()

		except socket.error as msg:
			logging.error(msg)
		except Exception, e:
			logging.info(e)
		finally:
			self.dns_server.close()
			logging.info('DNS server destory success...')

	def handler(self,data,addr):
		'''
		收到DNS数据后，进行处理请求，并将数据回发给客户
		这里的Cache是指 
		在第一次访问后，我们会封装response到DNSPacket。
		1. 对于大网页，第二个dns请求包直接从cache中取。 
		2. 对于多用户请求同一网页，服务端会直接从Cache中取
		3. 对于单用户请求同一网页，服务端会直接从Cache中取
		当然，大部分2，3情况，客户端会直接从各地的缓存服务器中获得数据
		'''
		request = DNSRecord.parse(data)
		data = str(request.q.qname)
		httpheader,index = parse_hostname(data,self.topdomain).next()# 服务端处理多个DNS请求 
		method,path,protocol = self.get_header(httpheader)
		if self.check_cache(path):
			DNSreply = self.DNS_Cache.get(path)
			reply = DNSreply.GetDNSreply(request,index)
			logging.debug("Cache reply:{0}".format(index))
			self.dns_server.sendto(reply,addr)
		else:#缓存没有命中
			response = self.http_server(method,path,protocol)
			DNSreply = DNSPacket(response)
			DNSreply.makereply()
			self.DNS_Cache[path]= DNSreply
			reply = DNSreply.GetDNSreply(request,index)
			print len(reply)
			logging.debug("No Cache reply:{0}".format(index))
			self.dns_server.sendto(reply,addr)
		return True

	def start_dns_server(self):
		'''
		监听DNS端口
		'''
		dns_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		dns_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		dns_server.bind(self.ludp_addr)
		logging.info("DNS Server {0} Listening Success...".format(self.ludp_addr))
		return dns_server

	def get_header(self,data):
		data = data.split()
		return data

	def http_server(self,method,path,protocol):
		if method =='GET':
			res = self.method_GET(path)
		else:
			res = self.method_others()
		response = encode(res.content)
		return response

	def method_GET(self,path):
		r = requests.get(path)
		return r

	def method_others(self):
		pass

	def check_cache(self,path):
		return self.DNS_Cache.has_key(path)


def start_server():
	server = Server(LUDP_ADDR,'xiaoxi.wanmitech.com')
	server.main_loop()

if __name__ == '__main__':
	start_server()


