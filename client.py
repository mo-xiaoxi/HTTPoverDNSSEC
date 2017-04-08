#!/usr/bin/env python
# encoding: utf-8

import sys
import socket
import logging
import threading
import base64

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
)

BUFSIZE = 1024
LTCP_ADDR = ('127.0.0.1',7890)
RUDP_ADDR = ('127.0.0.1',1234)
TIMEOUT = 2
MAX_RESEND_COUNT = 10
END_FLAG = 'DNSEND'

class Client(object):
	def __init__(self,ltcp_addr,rudp_addr):
		self.ltcp_addr = ltcp_addr
		self.rudp_addr = rudp_addr
		self.proxy_buffer = ''
		self.running = True
		self.timeout = TIMEOUT


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
		reSendCount = 0
		recvdata = ''
		header = self.get_header(connection)
		dns_udp_client ,dns_remote_addr = self.dns_client()
		dns_udp_client.sendto(header,dns_remote_addr)
		while True:
			try:
				recv,address = dns_udp_client.recvfrom(BUFSIZE)
				recvdata += recv
				if recv.find(END_FLAG)!=-1:
					recvdata = recvdata[:-6]
					response = self.decode(recvdata)
					connection.send(response)
					return  True
			except socket.timeout:
				logging.info("Timeout, Send again!")
				dns_udp_client.sendto(header,dns_remote_addr)
				reSendCount += 1
				if reSendCount > MAX_RESEND_COUNT:
					logging.error("Failed to send !something erorr ! please check the system !")
					return False
			except socket.error as msg:
				logging.error(msg)
			except Exception, e:
				logging.error(e)

	def decode(self,recv):
		return base64.b64decode(recv)
	
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

	def http2dns(self):
		pass

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
	client = Client(LTCP_ADDR,RUDP_ADDR)
	client.main_loop()

if __name__ == '__main__':
	start_client()


