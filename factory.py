# -*- coding: utf-8 -*-

import time
import inspect


class Factory(object):

	def create(self):
		raise NotImplementedError


class TimestampFactory(Factory):

	def create(self):
		return time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ": "


class SourceLocationFactory(Factory):

	def create(self):
		return inspect.stack()[1][3]


class ReturnFactory(Factory):

	def __init__(self, s):
		self.msg = s

	def create(self):
		return self.msg


class ConcatFactory(Factory):

	def __init__(self, fs):
		self.factories = fs

	def create(self):
		return ''.join(f.create() for f in self.factories)

