# -*- coding: utf-8 -*-


class RuleContext(object):

	def __init__(self, level, gender, month, day, items):
		self.level = level
		self.gender = gender
		self.month = month
		self.day = day
		self.items = items

	def getLevel(self):
		return self.level

	def getGender(self):
		return self.gender

	def getMonth(self):
		return self.month

	def getDay(self):
		return self.day

	def getItems(self):
		return self.items


class Result(object):
	def __init__(self):
		self.value = 1.0
		self.flag = False

	def getFlag(self):
		return self.flag

	def setFlag(self, flag):
		self.flag = flag

	def getValue(self):
		return self.value

	def setValue(self, value):
		self.value = value


class Rule(object):

	def apply(self, context, result):
		pass

	def and_rule(self, rule):
		return AndRule(self, rule)

	def then_rule(self, rule):
		return IfElseRule(self, rule, NilRule())

	@staticmethod
	def notrule(rule):
		return NotRule(rule)

	@staticmethod
	def andrule(rule1, rule2):
		return AndRule(rule1, rule2)

	@staticmethod
	def ifelse(cond, rule1, rule2):
		return IfElseRule(cond, rule1, rule2)

	@staticmethod
	def nil():
		return NilRule()

	@staticmethod
	def any(rules):
		return ExclusiveRule(rules)


class ExclusiveRule(Rule):

	def __init__(self, rules):
		self.rules = rules

	def apply(self, context, result):
		for rule in self.rules:
			if rule.apply(context, result):
				return True
		return False


class IfElseRule(Rule):

	def __init__(self, cond, consequence, alternative):
		self.cond = cond
		self.consequence = consequence
		self.alternative = alternative

	def apply(self, context, result):
		if self.cond.apply(context, result):
			return self.consequence.apply(context, result)
		else:
			return self.alternative.apply(context, result)


class NotRule(Rule):

	def __init__(self, rule):
		self.rule = rule

	def apply(self, context, result):
		if not self.rule.apply(context, result):
			return True
		return False


class AndRule(Rule):

	def __init__(self, rule1, rule2):
		self.rule1 = rule1
		self.rule2 = rule2

	def apply(self, context, result):
		if self.rule1.apply(context, result) and self.rule2.apply(context, result):
			return True
		else:
			return False


class NilRule(Rule):

	def apply(self, context, result):
		return False



class MemberDiscountRule(Rule):

	def __init__(self, level, discount):
		self.level = level
		self.discount = discount

	def apply(self, context, result):
		if context.getLevel() == self.level:
			result.setValue(result.getValue() * (1.0 - self.discount))
			return True
		return False


class GenderRule(Rule):

	def __init__(self, gender):
		self.gender = gender

	def apply(self, context, result):
		if context.getGender() == self.gender:
			return True
		else:
			return False


class MonthRule(Rule):

	def __init__(self, month):
		self.month = month

	def apply(self, context, result):
		if context.getMonth() == self.month:
			return True
		else:
			return False


class DayRule(Rule):

	def __init__(self, day):
		self.day = day

	def apply(self, context, result):
		if context.getDay() == self.day:
			return True
		else:
			return False


class DiscountRule(Rule):

	def __init__(self, discount):
		self.discount = discount

	def apply(self, context, result):
		result.setValue(result.getValue() * (1-self.discount))
		return True


class PurchasedRule(Rule):

	def __init__(self, items):
		self.items = items

	def apply(self, context, result):
		items = context.getItems()
		if all(item in items for item in self.items):
			return True
		else:
			return False


class ProductDoubleRule(Rule):

	def __init__(self, rules):
		self.rules = rules

	def apply(self, context, result):
		for rule in self.rules:
			rule.apply(context, result)
		return True


def createRule():
	gold_member = MemberDiscountRule('gold', 0.1)
	silver_member = MemberDiscountRule('silver', 0.05)
	platinum_member = MemberDiscountRule('platinum', 0.2)
	by_member = Rule.any([platinum_member, gold_member, silver_member])

	is_female = GenderRule('female')
	is_female_day = MonthRule(3).and_rule(DayRule(8))
	female_discount = is_female.and_rule(is_female_day).then_rule(DiscountRule(0.05))

	tv_speaker = PurchasedRule(['tv', 'speaker']).then_rule(DiscountRule(0.05))
	tv_speaker_dvd = PurchasedRule(['tv', 'speaker', 'dvd']).then_rule(DiscountRule(0.07))
	by_purchase = Rule.any([tv_speaker_dvd, tv_speaker])

	final_discount = ProductDoubleRule([by_member, female_discount, by_purchase])
	return final_discount


if __name__ == '__main__':

	rule = createRule()

	context1 = RuleContext('gold', 'female', 1, 1, ["tv","speaker","dvd"])
	result1 = Result()
	print rule.apply(context1, result1)
	print result1.getValue()

	context2 = RuleContext('gold', 'female', 3, 8, ["tv","speaker","dvd"])
	result2 = Result()
	print rule.apply(context2, result2)
	print result2.getValue()
	print result2.getValue() == 0.837*0.95
