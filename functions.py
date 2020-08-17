# -*- coding: utf-8 -*-


class Function(object):

	def __init__(self, rtype, pcount, func):
		self.rtype = rtype
		self.pcount = pcount
		self.func = func

	def getReturnType(self):
		return self.rtype

	def getParameterCount(self):
		return self.pcount

	def call(self, *args):
		return self.func(*args)


# class Functions(object):
#
# 	ctor = Function()


def ctor(typ):
	return Function(typ, 1, typ)