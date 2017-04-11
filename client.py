#!/usr/bin/env python
# encoding: utf-8
__Author__ = 'moxiaoxi'

import socket
import logging
import threading
import base64
import hashlib
import dns.resolver
from  encoding import *

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s',
)

BUFSIZE = 1460
LTCP_ADDR = ('127.0.0.1',7890)
RUDP_ADDR = ('106.14.61.185',1234)
MAX_RESEND_COUNT = 10
END_FLAG = 'DNSEND'
TUNNEL_DOMAIN = 'xiaoxi.wanmitech.com'
NAMESERVER = '8.8.8.8'

class Client(object):
	def __init__(self,ltcp_addr,rudp_addr,topdomain,nameservers=NAMESERVER,dnstype='TXT',timeout=5,MaxresendCount=5):
		self.ltcp_addr = ltcp_addr
		self.rudp_addr = rudp_addr
		self.proxy_buffer = ''
		self.running = True
		self.topdomain = topdomain
		self.resolver = dns.resolver.Resolver()
		self.nameservers = nameservers
		self.resolver.nameservers = [nameservers]
		self.dnstype = dnstype
		self.resolver.timeout= timeout
		self.res = ''
		self.MaxresendCount = MaxresendCount
		self.first = True

	def main_loop(self):
		try:
			self.proxy = self.start_http_proxy()
			while True:
				http_proxy_thread = threading.Thread(target=self.handler,args=self.proxy.accept())
				http_proxy_thread.daemon = True
				http_proxy_thread.start()

		except socket.error as msg:
			logging.error(msg)
		except Exception, e:
			logging.info(e)
		finally:
			self.proxy.close()
			logging.info('HTTP proxy destory success...')


	def handler(self,connection,address):
		'''
		处理HTTP over DNS的主要逻辑
		'''
		http_header = self.get_header(connection)
		dns_hostname = build_hostname(http_header,self.topdomain)#使用迭代器构造多个dns请求 处理大内容的网页
		hostname = dns_hostname.next()
		#处理第一个数据包
		UDPcount,index,res = self.query(hostname)
		data = [None]*UDPcount
		data[index] = res #第一个包处理完毕
		# 发起多线程获取数据
		while(None in data):
			hostname = dns_hostname.next()
			UDPcount,index,res = self.query(hostname)
			data[index] = res
		response = ''.join(data)
		response = decode(response)
		connection.send(response)
		return True

	def query(self,hostname):
		error_flag = False
		UDPcount = 0
		index = 0
		while True:
			response = self.send_dns_query(hostname)#第一个数据包请求
			if response == None:
				continue #丢包了,再发
			res = ''
			for i in response:
				UDPcount,index,restmp = self.parse_response(i)
				if(index < 0):
					print 1
					error_flag = True
					continue
				res += restmp
			if(error_flag == False):
				break
		return UDPcount,index,res


	def send_dns_query(self,hostname):
		resendCount = 0
		while True:
			try:
				answers = self.resolver.query(hostname,self.dnstype)
				break
			except dns.exception.DNSException as msg:
				logging.debug(msg)
				logging.info('DNS packet missed,so we resend it !time:{0}'.format(resendCount))
				resendCount += 1
				if(resendCount >= self.MaxresendCount):
					logging.error('Failed to Resend !something erorr ! please check the system !')
					return None
		logging.debug("DNS answer :{0}".format(answers))
		response = []
		for rdata in answers:
			tmp = str(rdata).lstrip('"').rstrip('"')
			response.append(tmp)
		return response



	def parse_response(self,response):#第一个数据回复包处理
		if(self.check_packet(response)):
			i = parse_flag(response[33])
		else:
			logging.warning('Packet crashed,resend it!')
			i = -1#packet error
		UDPcount = parse_flag(response[32])
		res = response[34:]
		return UDPcount,i,res


	def start_http_proxy(self):
		'''
		初始化TCP socket 用于作为本地HTTP代理
		'''
		proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			proxy.bind(self.ltcp_addr)
			proxy.listen(0)
			logging.info("HTTP Proxy Client {0} Listening Success...".format(self.ltcp_addr))
			return proxy
		except socket.error as msg:
			logging.error(msg)
		except Exception, e:
			logging.error(e)
	
	def get_header(self,connection):
		data = ''
		while True:
			data += connection.recv(BUFSIZE)
			end = data.find('\n')
			if end!=-1:
				break
		header = (data[:end+1]).split()
		if header[2].find('HTTPS') != -1:
			logging.error("NOT HTTP!!!")
		data = data[:end+1] #just for debug
		logging.info("HTTP:{0}".format(data))
		return data
	
	def check_packet(self,data):
		if(data[:32] == hashlib.md5(data[32:]).hexdigest()):
			return True
		else:
			return False

def start_client():
	client = Client(LTCP_ADDR,RUDP_ADDR,TUNNEL_DOMAIN)
	client.main_loop()

if __name__ == '__main__':
	start_client()


