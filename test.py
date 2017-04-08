#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests

proxies = {
	"http":"http://127.0.0.1:7890"
}
res = requests.get("http://45.62.96.72/test.html",proxies=proxies)
# res = requests.get("http://45.62.96.72/test.html")
print res.content