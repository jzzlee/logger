# -*- coding: utf-8 -*-


class NeptuneException(Exception):

	def printExecutionTrace(self, writer):
		pass


class JaskellException(Exception):
	def printEvaluationTrace(self, writer):
		pass
