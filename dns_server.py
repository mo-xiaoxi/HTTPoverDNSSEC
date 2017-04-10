#!/usr/bin/env python
# encoding: utf-8

import sys
import socket
import logging
import threading
import requests
import base64
from dnslib import DNSRecord,QTYPE,DNSHeader,RR,TXT


logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
)

BUFSIZE = 255
LUDP_ADDR = ('0.0.0.0',53)
TIMEOUT = 20
MAX_RESEND_COUNT = 10
TTL = 100
DNSBUF = 3000
class Server(object):
	def __init__(self,ludp_addr,topdomain):
		self.ludp_addr = ludp_addr
		self.running = True
		self.timeout = TIMEOUT
		self.topdomain = topdomain

	def start_dns_server(self):
		'''
		监听DNS端口
		'''
		dns_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		dns_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		dns_server.bind(self.ludp_addr)
		logging.info("DNS Server {0} Listening Success...".format(self.ludp_addr))
		return dns_server


	def dns2http(self):
		pass

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
			logging.info('connection destory success...')

	def get_header(self,data):
		data = data.split()
		return data

	def handler(self,data,addr):
		'''
		收到DNS数据后，进行处理请求，并将数据回发给客户
		'''
		request = DNSRecord.parse(data)
		data = str(request.q.qname)
		httpheader = self.parse_hostname(data,self.topdomain)
		response = self.http_server(httpheader)
		reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
		#进行多个包拆分回复
		response += 'DNSEND'
		l = len(response)
		t = l/BUFSIZE + 1
		for i in range(t):
			packet = response[BUFSIZE*i:BUFSIZE*(i+1)]
			reply.add_answer(RR(rname=request.q.qname, rtype=QTYPE.TXT, rclass=1, ttl=TTL, rdata=TXT(packet)))
			#logging.info('packet:{0},{1}'.format(i,packet))
			self.dns_server.sendto(reply.pack(),addr)
		print reply.pack(),len(reply.pack())
		print dir(reply)
		# self.dns_server.sendto(reply.pack(),addr)
		return True


	def http_server(self,httpheader):
		method,path,protocol = self.get_header(httpheader)
		if method =='GET':
			res = self.method_GET(path)
		else:
			res = self.method_others()
		response = self.encode(res.content)
		return response

	def parse_hostname(self,data,topdomain):
		buf = data[:-len(topdomain)-1-1]#去除自定义域名的前缀和后缀dot
		buf = buf.split('.')
		tmp = ''
		for i in buf:
			tmp +=i
		buf = self.decode(tmp)
		return buf
		

	def method_GET(self,path):
		r = requests.get(path)
		return r

	def method_others(self):
		pass

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

def start_server():
	server = Server(LUDP_ADDR,'xiaoxi.wanmitech.com')
	server.main_loop()

if __name__ == '__main__':
	start_server()


