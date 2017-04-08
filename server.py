#!/usr/bin/env python
# encoding: utf-8

import sys
import socket
import logging
import threading
import requests
import base64

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
)

BUFSIZE = 1024
LUDP_ADDR = ('127.0.0.1',1234)
TIMEOUT = 2
MAX_RESEND_COUNT = 10

class Server(object):
	def __init__(self,ludp_addr):
		self.ludp_addr = ludp_addr
		self.running = True
		self.timeout = TIMEOUT

	def start_dns_server(self):
		dns_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		dns_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		dns_server.bind(self.ludp_addr)
		logging.info("DNS Server {0} Listening Success...".format(self.ludp_addr))
		return dns_server


	def dns2http(self):
		try:
			self.dns_server = self.start_dns_server()
			while True:
				http_proxy_thread = threading.Thread(target=self.handler,args=self.dns_server.recvfrom(BUFSIZE))
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
		print data,addr
		method,path,protocol = self.get_header(data)
		print path
		if method =='GET':
			res = self.method_GET(path)
		else:
			res = self.method_others()
		response = self.encode(res.content)
		self.sendPacket(response,addr)
		return True

	def sendPacket(self,response,addr):
		response += 'DNSEND'
		l = len(response)
		t = l/BUFSIZE + 1
		for i in range(t):
			pakctet = response[BUFSIZE*i:BUFSIZE*(i+1)]
			self.dns_server.sendto(pakctet,addr)
		return True

	def method_GET(self,path):
		r = requests.get(path)
		return r

	def method_others(self):
		pass

	def encode(self,content):
		return base64.b64encode(content)


def start_server():
	server = Server(LUDP_ADDR)
	server.dns2http()

if __name__ == '__main__':
	start_server()


