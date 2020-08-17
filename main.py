# -*- coding: utf-8 -*-

from container import *


class A(object):

	def __init__(self, x):
		self.x = x

	def isx(self):
		return self.x


class B(object):
	pass

# b_com = Component


class X(object):

	def __init__(self):
		self.value = 'create by X'


class Y(object):

	def __init__(self, a):
		self.a = a

	def getX(self):
		x = X()
		x.value = 'create by Y'
		return x


def createX(aisx):
	a_com = WithArgumentComponent(Components.ctor(A), 0, Components.value(aisx))

	class _Binder1(Binder):

		def bind(self, a):
			isx_com = Components.method(a, "isx")
			class _Binder2(Binder):
				def bind(self, isx):
					if isx:
						return Components.value(X())
					else:
						y_com = WithArgumentComponent(Components.ctor(Y), 0, Components.value(a))

						class _Binder(Binder):
							def bind(self, y):
								ss = Components.method(y, "getX")
								return ss

						return BinderComponent(y_com, _Binder())
			return BinderComponent(isx_com, _Binder2())

	return BinderComponent(a_com, _Binder1()).create(None)


if __name__ == '__main__':
	x1 = createX(False)
	print x1.value

	x2 = createX(True)
	print x2.value
