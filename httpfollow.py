#!/usr/bin/env python

"""
httpfollow http://www.example.com -c 1024
httpfollow http://www.example.com -c 2000 -f
"""
import base64, re, time, sys, argparse
from urllib2 import Request, URLError, HTTPError, urlopen, HTTPBasicAuthHandler
from urlparse import urlparse, urlsplit, SplitResult

class HttpFollow:
	def __init__(self, url, options):
		self.options = options
		self.position = None
		self._parseurl(url)
		self._prepare()

	def _parseurl(self, url):
		ret = urlsplit(url)
		self.username = ret.username
		self.password = ret.password
		if ret.port <> None:
			n = SplitResult(ret.scheme, ret.hostname + ":" + ret.port.__str__(), ret.path, ret.query, ret.fragment)
		else:
			n = SplitResult(ret.scheme, ret.hostname, ret.path, ret.query, ret.fragment)
		self.url = n.geturl()

	def _prepare(self):
		self.fetcher = Request(self.url)
		if(self.username <> None and self.password <> None):
			base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
			self.fetcher.headers["Authorization"] = "Basic %s" % base64string

	def fetch_range(self, begin, end):
		if begin <> None and end <> None:
			self.fetcher.headers["Range"] = 'bytes=%s-%s' % (begin, end)
		elif begin <> None and end == None:
			self.fetcher.headers["Range"] = 'bytes=%s-' % (begin)
		elif begin == None and end <> None:
			self.fetcher.headers["Range"] = 'bytes=-%s' % (end)

		f = urlopen(self.fetcher)
		d = f.read()
		if f.code == 206:
			crange = f.headers['Content-Range']
			m = re.search("^.*\/(\d*)$", crange)
			pos = int(m.group(1)) - 1
			if pos <> self.position:
				self.position = pos
				print d
		elif f.code == 200:
			self.position = len(d)
			print d
		else:
			print f.headers
			print d

	def fetch(self):
		self.fetch_range(None, options.c)
		while options.f:
			self.fetch_range(self.position, None)
			time.sleep(1)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('url', metavar='URL')
	parser.add_argument('-f', action='store_const', const=True)
	parser.add_argument('-c', type=int, metavar='number', default=1024)
	options = parser.parse_args()

	try:
		httpfollow = HttpFollow(options.url, options)
		httpfollow.fetch()
	except KeyboardInterrupt:
		pass

