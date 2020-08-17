# -*- coding: utf-8 -*-

import functions


class Dependency(object):

	def getArgument(self, i, typ):
		pass

	def verifyArgument(self, i):
		pass

	def getProperty(self, i):
		pass

	def verifyProperty(self, i):
		pass

	def getContainer(self):
		return Container


class Component(object):

	def getType(self):
		pass

	def create(self, dep):
		pass

	def verify(self, dep):
		pass

	def bind(self, binder):
		pass


class Container(object):

	Components = {}

	@staticmethod
	def getComponent(key):
		return Container.Components.get(key, None)

	@staticmethod
	def addComponent(key, com):
		Container.Components[key] = com

	@staticmethod
	def getComponentOfType(typ):
		pass


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
		args = [dep.getArgument(i, None) for i in range(count)]
		return self.function.call(*args)

	def verify(self, dep):
		count = self.function.getParameterCount()
		verified = all(dep.verifyArgument(i) for i in xrange(count))
		return self.function.getReturnType()

	def bind(self, binder):
		"""
		:type binder: ParameterBinder
		:return:
		"""
		return ValueComponent(self.create(ParameterBinderDependency(None, binder)))


class BeanComponent(Component):

	def __init__(self, typ):
		self.type = typ

	def getType(self):
		return self.type

	def create(self, dep):
		return self.type()

	def verify(self, dep):
		return self.getType()


class UseKeyComponent(Component):

	def __init__(self, key):
		self.key = key

	def create(self, dep):
		"""
		:type dep: Dependency
		"""
		c = dep.getContainer().getComponent(self.key)   # type: Component
		if c is None:
			raise KeyError('component key %s not found' % self.key)
		return c.create(dep)


class UseArgumentComponent(Component):

	def __init__(self, i, typ):
		self.index = i
		self.typ = typ

	def create(self, dep):
		return dep.getArgument(self.index, self.typ)


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

	@staticmethod
	def use_key(key):
		return UseKeyComponent(key)

	@staticmethod
	def use_argument(i, typ):
		return UseArgumentComponent(i, typ)

	@staticmethod
	def with_argument(com, i, arg):
		"""
		:type com: Component
		:param i:
		:type arg: Component
		:return:
		"""
		class _ParameterBinder(ParameterBinder):
			def bind(self, k, typ):
				if k == i:
					return arg
				else:
					return Components.use_argument(k, typ)
		return com.bind(_ParameterBinder())

	@staticmethod
	def with_arguments(com, args):
		"""
		:type com: Component
		:type args: list of Component
		:return:
		"""
		class _ParameterBinder(ParameterBinder):
			def bind(self, i, typ):
				return args[i]
		return com.bind(_ParameterBinder())


class ParameterBinder(object):

	def bind(self, i, typ):
		"""
		:param i:
		:return: Component
		"""
		pass


class ParameterBinderDependency(Dependency):
	def __init__(self, dep, binder):
		self.dep = dep          # type: Dependency
		self.binder = binder    # type: ParameterBinder

	def getArgument(self, i, typ):
		return self.binder.bind(i, typ).create(self.dep)


class ParameterBinderComponent(Component):

	def __init__(self, com, binder):
		self.com = com          # type: Component
		self.binder = binder    # type: ParameterBinder

	def create(self, dep):
		return self.com.create(ParameterBinderDependency(dep, self.binder))

