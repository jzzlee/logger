# -*- coding: utf-8 -*-

import functions


class Dependency(object):

	def getArgument(self, i):
		pass

	def verifyArgument(self, i):
		pass

	def getProperty(self, i):
		pass

	def verifyProperty(self, i):
		pass


class Component(object):

	def getType(self):
		pass

	def create(self, dep):
		pass

	def verify(self, dep):
		pass


class Container(object):

	def getComponent(self, key):
		raise NotImplementedError

	def getComponentOfType(self, typ):
		raise NotImplementedError


class ValueComponent(Component):

	def __init__(self, v):
		self.value = v

	def getType(self):
		return self.value.__class__

	def create(self, dep):
		return self.value

	def verify(self, dep):
		return self.getType()


class FunctionComponent(Component):

	def __init__(self, f):
		self.function = f   # type: functions.Function

	def getType(self):
		return self.function.getReturnType()

	def create(self, dep):
		"""
		:type dep: Dependency
		"""
		count = self.function.getParameterCount()
		args = [dep.getArgument(i) for i in range(count)]
		return self.function.call(*args)

	def verify(self, dep):
		count = self.function.getParameterCount()
		verified = all(dep.verifyArgument(i) for i in xrange(count))
		return self.function.getReturnType()


class BeanComponent(Component):

	def __init__(self, typ):
		self.type = typ

	def getType(self):
		return self.type

	def create(self, dep):
		return self.type()

	def verify(self, dep):
		return self.getType()


class WithArgumentComponent(Component):
	def __init__(self, parent, pos, arg):
		self.parent = parent
		self.pos = pos
		self.arg = arg

	def getType(self):
		return self.parent.getType()

	def create(self, dep):
		return self.parent.create(self.withArg(dep))

	def verify(self, dep):
		return self.parent.verify(self.withArg(dep))

	def withArg(self, dep):
		pos = self.pos
		arg = self.arg
		class _Dependency(Dependency):
			def getArgument(self, i):
				if i == pos:
					return arg.create(dep)
				else:
					return dep.getArgument(i)

		return _Dependency()


class WithPropertyComponent(Component):

	def __init__(self, parent, key, prop):
		self.parent = parent    # type: Component
		self.key = key          # type: str
		self.prop = prop        # type: Component

	def getType(self):
		return self.parent.getType()

	def create(self, dep):
		return self.parent.create(self.withProp(dep))

	def verify(self, dep):
		return self.parent.verify(self.withProp(dep))

	def withProp(self, dep):
		def getProp(_, k, typ, this=self):
			if k == self.key:
				return self.prop.create(dep)
			else:
				return dep.getProperty(k, typ)

		ndep = Dependency()
		ndep.getProperty = getProp


class Map(object):

	def map(self, obj):
		pass


class MapComponent(Component):

	def __init__(self, com, mapper):
		self.com = com          # type: Component
		self.mapper = mapper    # type: Map

	def getType(self):
		return None

	def create(self, dep):
		return self.mapper.map(self.com.create(dep))

	def verify(self, dep):
		self.com.verify(dep)
		return object.__class__


class Binder(object):

	def bind(self, obj):
		pass


class BinderComponent(Component):

	def __init__(self, com, binder):
		self.com = com          # type: Component
		self.binder = binder    # type: Binder

	def getType(self):
		return None

	def create(self, dep):
		return self.binder.bind(self.com.create(dep)).create(dep)

	def verify(self, dep):
		self.com.verify(dep)
		return object.__class__


class SingletonComponent(Component):

	def __init__(self, com, val):
		self.com = com          # type: Component
		self.value = val        # type: object

	def getType(self):
		return self.com.getType()

	def create(self, dep):
		if self.value is not None:
			return self.value
		self.value = self.com.create(dep)
		return self.value

	def verify(self, dep):
		if self.value is not None:
			return self.value.__class__
		return self.com.verify(dep)


class Components(object):

	@staticmethod
	def static_method(clazz, methodName):
		method = getattr(clazz, methodName, None)
		return ValueComponent(method() if method else None)

	@staticmethod
	def ctor(clazz):
		return FunctionComponent(functions.ctor(clazz))

	@staticmethod
	def method(obj, methodName):
		method = getattr(obj, methodName, None)
		return ValueComponent(method() if method else None)

	@staticmethod
	def value(obj):
		return ValueComponent(obj)
