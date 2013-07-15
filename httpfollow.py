#!/usr/bin/env python

"""
httpfollow http://www.example.com 1024
"""
import base64, re, time, sys, argparse
from urllib2 import Request, URLError, HTTPError, urlopen, HTTPBasicAuthHandler
from urlparse import urlparse, urlsplit, SplitResult

class HttpFollow:
	def __init__(self, url, lsize):
		self.lsize = lsize
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

		try:
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
			return True
		except URLError, msg:
			print msg
			return False
		except HTTPError, msg:
			print msg
			return False

	def fetch(self):
		while True:
			ret = False
			if self.position == None:
				ret = self.fetch_range(None, self.lsize)
			else:
				ret = self.fetch_range(self.position, None)
			if ret == False:
				break
			time.sleep(1)

if __name__ == '__main__':
	script, url, lsize = sys.argv
	httpfollow = HttpFollow(url, lsize)
	try:
		httpfollow.fetch()
	except KeyboardInterrupt:
		pass

