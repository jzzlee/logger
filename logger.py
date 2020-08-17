# -*- coding: utf-8 -*-

import time
from exception import *


class LogLevel(object):
	__slots__ = ()

	VERBOSE = 0
	DEBUG = 1
	INFO = 2
	WARNING = 3
	ERROR = 4
	FATAL = 5


class Logger(object):

	def prints(self, level, msg):
		raise NotImplementedError

	def println(self, level, msg):
		raise NotImplementedError

	def printException(self, e):
		raise NotImplementedError


class NopLogger(Logger):

	def prints(self, level, msg):
		pass

	def println(self, level, msg):
		pass

	def printException(self, e):
		pass


class WriterLogger(Logger):

	def __init__(self, writer):
		self.writer = writer

	def prints(self, level, msg):
		self.writer.write(msg)

	def println(self, level, msg):
		self.writer.writeline(msg)

	def printException(self, e):
		e.printStackTrace(self.writer)


class SequenceLogger(Logger):

	def __init__(self, loggers):
		self.loggers = loggers

	def prints(self, level, msg):
		for logger in self.loggers:
			logger.prints(level, msg)

	def println(self, level, msg):
		for logger in self.loggers:
			logger.println(level, msg)

	def printException(self, e):
		for logger in self.loggers:
			logger.printException(e)


class FilteredLogger(Logger):

	def __init__(self, logger1, logger2, level):
		self.logger1 = logger1
		self.logger2 = logger2
		self.lv = level

	def prints(self, level, msg):
		self.logger1.prints(level, msg) if level == self.lv else self.logger2.prints(level, msg)

	def println(self, level, msg):
		self.logger1.println(level, msg) if level == self.lv else self.logger2.println(level, msg)

	def printException(self, e):
		self.logger1.printException(e) if self.lv == LogLevel.ERROR else self.logger2.printException(e)


class IgnoringLogger(Logger):

	def __init__(self, logger1, logger2, lv):
		self.logger1 = logger1
		self.logger2 = logger2
		self.lv = lv

	def prints(self, level, msg):
		self.logger1.prints(level, msg) if level >= self.lv else self.logger2.prints(level, msg)

	def println(self, level, msg):
		self.logger1.println(level, msg) if level >= self.lv else self.logger2.println(level, msg)

	def printException(self, e):
		self.logger1.printException(e) if self.lv >= LogLevel.ERROR else self.logger2.printException(e)


class ErrorMessageLogger(Logger):

	def __init__(self, writer, logger):
		self.writer = writer
		self.logger = logger

	def prints(self, level, msg):
		self.logger.prints(level, msg)

	def println(self, level, msg):
		self.logger.println(level, msg)

	def printException(self, e):
		self.writer.writeline(e.message)


class NeptuneExceptionLogger(Logger):

	def __init__(self, writer, logger):
		self.writer = writer
		self.logger = logger

	def prints(self, level, msg):
		self.logger.prints(level, msg)

	def println(self, level, msg):
		self.logger.println(level, msg)

	def printException(self, e):
		e.printExecutionTrace(self.writer) if isinstance(e, NeptuneException) else self.logger.printException(e)


class JaskellExceptionLogger(Logger):

	def __init__(self, writer, logger):
		self.writer = writer
		self.logger = logger

	def prints(self, level, msg):
		self.logger.prints(level, msg)

	def println(self, level, msg):
		self.logger.println(level, msg)

	def printException(self, e):
		e.printEvaluationTrace(self.writer) if isinstance(e, JaskellException) else self.logger.printException(e)


class TimestampLogger(Logger):

	def __init__(self, logger):
		self.logger = logger
		self.freshline = True

	def printTimestamp(self, level):
		if self.freshline:
			self.logger.prints(level, time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ": ")

	def prints(self, level, msg):
		self.printTimestamp(level)
		self.logger.prints(level, msg)
		self.freshline = False

	def println(self, level, msg):
		self.printTimestamp(level)
		self.logger.println(level, msg)
		self.freshline = True

	def printException(self, e):
		self.printTimestamp(LogLevel.ERROR)
		self.logger.printException(e)
		self.freshline = True


class PrefixLogger(Logger):

	def __init__(self, logger, factory):
		self.logger = logger
		self.factory = factory
		self.freshline = True

	def prefix(self, level):
		if self.freshline:
			prefix = self.factory.create()
			if prefix:
				self.logger.prints(level, prefix)
			self.freshline = False

	def prints(self, level, msg):
		self.prefix(level)
		self.logger.prints(level, msg)

	def println(self, level, msg):
		self.prefix(level)
		self.logger.println(level, msg)
		self.freshline = True

	def printException(self, e):
		self.prefix(LogLevel.ERROR)
		self.logger.printException(e)
		self.freshline = True


class Loggers(object):

	@staticmethod
	def nop():
		return NopLogger()

	@staticmethod
	def printwriter(writer):
		return WriterLogger(writer)

	@staticmethod
	def streamwriter(writer):
		return WriterLogger(writer)

	@staticmethod
	def filter(logger1, logger2, lv):
		return FilteredLogger(logger1, logger2, lv)

	@staticmethod
	def ignore(logger1, logger2, lv):
		return IgnoringLogger(logger1, logger2, lv)

	@staticmethod
	def errormsg(writer, logger):
		return ErrorMessageLogger(writer, logger)

	@staticmethod
	def neptune(writer, logger):
		return NeptuneExceptionLogger(writer, logger)

	@staticmethod
	def jaskell(writer, logger):
		return JaskellExceptionLogger(writer, logger)

	@staticmethod
	def timestamp(logger):
		return TimestampLogger(logger)



