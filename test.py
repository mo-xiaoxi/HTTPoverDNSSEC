#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import binascii
from dnslib import DNSRecord
proxies = {
	"http":"http://127.0.0.1:7890",
	# "https":"https://127.0.0.1:7890"
}
# res = requests.get("http://45.62.96.72/test2.html",proxies=proxies)
# res = requests.get("https://www.baidu.com",proxies=proxies)
res = requests.get("http://45.62.96.72/test2.html",proxies=proxies)
print res.content


# import socket

# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.sendto('test',('106.14.61.185',53))

# # from random import Random
# # def random_str(randomlength=8):
# #     str = ''
# #     chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
# #     length = len(chars) - 1
# #     random = Random()
# #     for i in range(randomlength):
# #         str+=chars[random.randint(0, length)]
# #     return str

# # print random_str(256)
# packet = binascii.unhexlify(b'45140054500d40003311a45dd043db0f6a0e3db9b78a003500406c6ff3c000000001000000000001066447567a6441067869616f78690977616e6d697465636803636f6d000010000100002904e4000000000000')
# print packet
# #d = DNSRecord.parse(packet)



