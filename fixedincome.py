
import re
from datetime import datetime
from math import exp


def enum(**enums):
	return type('Enum', (), enums)


def Period(pspec):
	"""
	period function parses the period specification string and return a 
	PSpec class instance.
	
		p = period('15 days')
		p = period('1 month')
		p = period('2.5 months')
		p = period('22.55 months')
		p = period('1.5 years')
		p = period('1.5 quarters')
		p = period('2012-07-12:2012-07-16')
		p = period( ("2012-7-12", "2012-7-22") )
		p = period('2012-12-12:2012-10-16')
		p = period('2012-07-12:2012-07-22')
	"""
	
	if type(pspec) is str:
		m = re.match('^(\d+)(\.\d+)? (year|half-year|quarter|month|day)s?$', pspec)
		if m:
			istimerange = False
		elif len(pspec.split(':')) == 2:
			(start, end) = pspec.split(':')
			istimerange = True
		else:
			raise Exception('Invalid period specitication')
	elif type(pspec) is tuple:
		if len(pspec) == 2:
			(start, end) = pspec
		else:
			raise Exception('Invalid period specitication')
		istimerange = True
	else:
		raise Exception('Invalid period specitication')
	
	ps = PSpec()
	if istimerange:
		dates = (datetime.strptime(start, '%Y-%m-%d'), 
			datetime.strptime(end, '%Y-%m-%d'))
		if dates[0] > dates[1]:
			raise Exception('Invalid period specitication: start date must be greater than end date.')
		# self.numberof = (self.dates[1] - self.dates[0]).days
		return DateRangePeriod(dates, 'day')
		# ps._fixed_numberof = None
		# ps.unit = 'day'
	else:
		g = m.groups()
		# ps._fixed_numberof = float(g[0] + (g[1] or '.0'))
		# ps.unit = g[2]
		return FixedTimePeriod(float(g[0] + (g[1] or '.0')), g[2])
	# return ps


class FixedTimePeriod(object):
	"""
	Period('1 year')
	Period('1 half-year')
	Period('1 quarter')
	Period('1 month')
	Period('1 day')
	"""
	def __init__(self, size, unit):
		self.calendar = None
		self.size = size
		self.unit = unit
		
	def numberof(self):
		"""docstring for __numberof"""
		return self.size
	
	def timefactor(self, daycount):
		"""
		Returns an year fraction regarding period definition.
		This function always returns year's fraction.
		"""
		days = self.numberof() * daycount.daysinbase/daycount.freqm[self.unit]
		return float(days)/daycount.daysinbase


class DateRangePeriod(object):
	"""
	d1 = "2012-07-12"
	d2 = "2012-07-27"
	Period( (d1, d2) )
	Period('2012-07-12:2012-07-16')
	Period((d1,d2), calANBIMA)
	Period('2012-07-12:2012-07-16', calANBIMA)
	
	For now we can consider only time unit as day but we should be completely 
	open to time units as month and year or even quarter. For example:
	Period('2012-04:2012-12') -> from april, 2012 to december, 2012: 9 months
	Period('2012-04:2012-12') -> from 2012 to 2012: 1 year

	Period('2012-1:2012-3') -> from 2012 first quarter to 2012 third one: 3 quarters
	I still don't know how to handle that!
	
	This procedure includes starting and ending points.
	"""
	def __init__(self, dates, unit='day', calendar=None):
		self.calendar = calendar
		self.dates = dates
		self.unit = unit
		
	def numberof(self):
		"""docstring for __numberof"""
		return (self.dates[1] - self.dates[0]).days
	
	def timefactor(self, daycount):
		"""
		Returns an year fraction regarding period definition.
		This functin always returns year fraction.
		"""
		days = self.numberof() * daycount.daysinbase/daycount.freqm[self.unit]
		return float(days)/daycount.daysinbase


class DayCount(object):
	"""docstring for DayCount"""
	DAYCOUNTS = {
		'30/360': None,
		'30/360 US': None,
		'30E/360 ISDA': None,
		'30E+/360': None, 
		'actual/actual ICMA': None,
		'actual/actual ISDA': None,
		'actual/365 Fixed': 365,
		'actual/360': 360,
		'actual/364': 364,
		'actual/365L': 365,
		'actual/actual AFB': None,
		'business/252': 252
	}
	
	def __init__(self, dc):
		self._daysinbase = self.DAYCOUNTS[dc]
		self.freqm = { # frequency multiplier
			'year': 1,
			'half-year': 2,
			'quarter': 4,
			'month': 12,
			'day': self._daysinbase
		}
	
	def __getdaysinbase(self):
		"""docstring for __getdaysinbase"""
		return self._daysinbase
	daysinbase = property(__getdaysinbase)
	

class Calendar(object):
	"""docstring for Calendar"""
	def __init__(self, arg):
		self.holidays = None # list of dates
		self.weekend_days = None # tuple of week days, usually (5,6) (sat,sun)
		# in Brazil we have ANBIMA's list of holidays so that we could use 
		# to manage business days computations
		# So that list has a start year and an ending year and
		# we have to consider that for setting startdate and enddate
		# startdate will be the first day of that start year and
		# enddate will be the last day of that end year
		self.startdate = None
		self.enddate = None
		
class Compounding(object):
	"""docstring for Compounding"""
	@staticmethod
	def simple(r, t):
		"""docstring for compounding_simple"""
		return 1 + r*t
	
	@staticmethod
	def compounded(r, t):
		"""docstring for compounding_compounded"""
		return (1 + r)**t
	
	@staticmethod
	def continuous(r, t):
		"""docstring for compounding_continuous"""
		return exp(r*t)


FREQ_MAP = {
	'annual': 'year',
	'semi-annual': 'half-year',
	'quarterly': 'quarter',
	'monthly': 'month',
	'daily': 'day'
}

# rate = '6%% annual simple (actual/365 Fixed)'
# rate = '0.09 annual compounded business/252 calANBIMA'
# rate = '0.06 annual continuous 30/360'

class InterestRate(object):
	"""docstring for InterestRate"""
	def __init__(self, rate, frequency, compounding, daycount, calendar=None):
		self.rate = rate
		self.frequency = frequency
		self.daycount = daycount
		self.compounding = compounding
		self.calendar = calendar
		self._compoundingfunc = getattr(Compounding, self.compounding)
		self._daycount = DayCount(self.daycount)
	
	def discount(self, period):
		"""docstring for discount"""
		return 1.0/compound(period)
	
	def compound(self, period):
		"""docstring for compound"""
		if type(period) is str:
			period = Period(period) # TODO: call Period passing calendar as parameter
		
		# tf = period.timefactor(self._daycount, self.calendar)
		tf = period.timefactor(self._daycount)
		t = tf * self._daycount.freqm[FREQ_MAP[self.frequency]]
		return self._compoundingfunc(self.rate, t)
	
	# write conversion functions: given other settings generate a different rate


