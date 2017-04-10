#!/usr/bin/env python
# encoding: utf-8

import sys
import socket
import logging
import threading
import base64
import dns.resolver

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
)

BUFSIZE = 512
LTCP_ADDR = ('127.0.0.1',7890)
RUDP_ADDR = ('106.14.61.185',1234)
MAX_RESEND_COUNT = 10
END_FLAG = 'DNSEND'
TUNNEL_DOMAIN = 'xiaoxi.wanmitech.com'
NAMESERVER = '8.8.8.8'

class Client(object):
	def __init__(self,ltcp_addr,rudp_addr,topdomain,nameservers=NAMESERVER,dnstype='TXT',timeout=2):
		self.ltcp_addr = ltcp_addr
		self.rudp_addr = rudp_addr
		self.proxy_buffer = ''
		self.running = True
		self.topdomain = topdomain
		self.resolver = dns.resolver.Resolver()
		self.nameservers = nameservers
		self.resolver.nameservers = [nameservers]
		self.dnstype = dnstype
		self.timeout = timeout


	def dns_client(self):
		'''
		初始化生成一个UDP Socket
		'''
		dns_udp_client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		dns_udp_client.settimeout(self.timeout)
		logging.info("Init DNS Client Success! Remote addr {0}...".format(self.rudp_addr))
		return dns_udp_client,self.rudp_addr

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

	def handler(self,connection,address):
		'''
		处理HTTP over DNS的主要逻辑
		'''
		http_header = self.get_header(connection)
		hostname = self.build_hostname(http_header,self.topdomain)
		count = 0 #尝试用count.域名的方式 进行多个域名请求 完成大网站的访问
		hostname = self.build_hostname(http_header,self.topdomain)
		while True:
			answers = self.resolver.query(hostname,self.dnstype)
			logging.info("DNS answer :{0}".format(answers))
			response = ''
			for rdata in answers:
				response += str(rdata)
			print response
			if response.find(END_FLAG)!=-1:
				response = response[:-6]
				response = self.decode(response)
				connection.send(response)
				break
		return True


	def encode(self,content):
		return self.base64u_encode(content)

	def decode(self,recv):
		return self.base64u_decode(recv)

	def base64u_encode(self,content):
		'''base64编码，=被舍去,+替换成_,/替换成-'''
		tmp = base64.b64encode(content)
		tmp = tmp.rstrip('=')
		tmp = tmp.replace('+','_')
		tmp = tmp.replace('/','-')
		return tmp

	def base64u_decode(self,recv):
		'''base64解码，=补上,_替换成+,-替换成/'''
		l = len(recv)%4
		tmp = recv+l*'='
		tmp = tmp.replace('_','+')
		tmp = tmp.replace('-','/')
		tmp = base64.b64decode(tmp)
		return tmp
	
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

	def build_hostname(self,data,topdomain,maxlen=0xFF):
		space = maxlen - len(topdomain)-3 # 1 dot before topdomain 2 saftey
		buf = self.encode(data)
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
			logging.info('connection destory success...')

def start_client():
	client = Client(LTCP_ADDR,RUDP_ADDR,TUNNEL_DOMAIN)
	client.main_loop()

if __name__ == '__main__':
	start_client()


