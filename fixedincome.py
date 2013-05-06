
import re
import os
from datetime import datetime, date, timedelta
from math import exp


def enum(**enums):
	return type('Enum', (), enums)


def Period(pspec):
	"""
	period function parses the period specification string and return a 
	PSpec class instance.
	
		p = Period('15 days')
		p = Period('1 month')
		p = Period('2.5 months')
		p = Period('22.55 months')
		p = Period('1.5 years')
		p = Period('1.5 quarters')
		p = Period('2012-07-12:2012-07-16')
		p = Period( ("2012-7-12", "2012-7-22") )
		p = Period('2012-12-12:2012-10-16')
		p = Period('2012-07-12:2012-07-22')
		p = Period('2012-07-12:2012-07-22 calANBIMA')
	"""
	
	if type(pspec) is str:
		m = re.match('^(\d+)(\.\d+)? (year|half-year|quarter|month|day)s?$', pspec)
		if m:
			istimerange = False
		elif len(pspec.split(':')) == 2:
			(start, end) = pspec.split(':')
			istimerange = True
		else:
			raise Exception('Invalid period specification')
	elif type(pspec) is tuple:
		if len(pspec) == 2:
			(start, end) = pspec
		else:
			raise Exception('Invalid period specification')
		istimerange = True
	else:
		raise Exception('Invalid period specification')
	
	if istimerange:
		dates = (datetime.strptime(start, '%Y-%m-%d').date(), 
			datetime.strptime(end, '%Y-%m-%d').date())
		if dates[0] > dates[1]:
			raise Exception('Invalid period specification: start date must be greater than end date.')
		return DateRangePeriod(dates, 'day')
	else:
		g = m.groups()
		return FixedTimePeriod(float(g[0] + (g[1] or '.0')), g[2])


FREQ_MAP = { # frequency to time unit mapping
	'annual': 'year',
	'semi-annual': 'half-year',
	'quarterly': 'quarter',
	'monthly': 'month',
	'daily': 'day'
}

class GenericPeriod(object):
	"""
	GenericPeriod class
	
	This class accommodates methods for time computing.
	"""
	
	def size(self):
		"""docstring for numberof"""
		raise NotImplementedError('The method numberof is not implemented for this \
			class. User FixedTimePeriod or DateRangePeriod instead.')
	

class FixedTimePeriod(GenericPeriod):
	"""
	Period('1 year')
	Period('1 half-year')
	Period('1 quarter')
	Period('1 month')
	Period('1 day')
	"""
	def __init__(self, size, unit):
		self._size = size
		self.unit = unit
		
	def size(self):
		"""Return the quantity related to the fixed period."""
		return self._size


class DateRangePeriod(GenericPeriod):
	"""
	d1 = "2012-07-12"
	d2 = "2012-07-27"
	Period((d1, d2))
	Period('2012-07-12:2012-07-16')
	
	For now we can consider only the *day* time unit but we should be completely 
	open to other time units such as *month* and *year* or even *quarter*. 
	For example:
	Period('2012-04:2012-12') -> from april, 2012 to december, 2012: 9 months
	Period('2012:2012') -> from 2012 to 2012: 1 year
	Period('2012-1:2012-3') -> from 2012 first quarter to 2012 third one: 3 quarters
	
	I still don't know how to handle that!
	
	This procedure includes starting and ending points.
	"""
	def __init__(self, dates, unit='day'):
		self.dates = dates
		self.unit = unit
		
	def size(self):
		"""Return the total amount of days between two dates"""
		return (self.dates[1] - self.dates[0]).days


class CalendarRangePeriod(DateRangePeriod):
	"""
	A CalendarRangePeriod is a DateRangePeriod which uses a Calendar to
	compute the amount of days contained into the underlying Period.
	"""
	def __init__(self, period, calendar):
		super(CalendarRangePeriod, self).__init__(period.dates, unit='day')
		self.calendar = calendar
	
	def size(self):
		'Return the amount of working days into period.'
		d1 = self.dates[0].isoformat()
		d2 = self.dates[1].isoformat()
		return self.calendar.workdays((d1, d2))


class DayCount(object):
	"""DayCount"""
	DAYCOUNTS = {
		'30/360': None,
		'30/360 US': None,
		'30E/360 ISDA': None,
		'30E+/360': None, 
		'actual/365 Fixed': 365,
		'actual/360': 360,
		'actual/364': 364,
		'actual/365L': 365,
		'business/252': 252
	}
	
	def __init__(self, dc):
		self._daysinbase = self.DAYCOUNTS[dc]
		self._unitsize = { # frequency multiplier
			'year': 1,
			'half-year': 2,
			'quarter': 4,
			'month': 12,
			'day': self._daysinbase
		}
	
	def __getdaysinbase(self):
		"""
		Private get method for the read-only property daysinbase.
		"""
		return self._daysinbase
	daysinbase = property(__getdaysinbase)
	
	def daysinunit(self, unit):
		"""
		timeunit method returns the amount of days in base, for a given time 
		unit (year, month, day, ...). For example, the business/252 day count 
		rule has 252 days in base, so if you have a period of time with a time
		unit of month then you use 21 days for each month.
		"""
		return float(self.daysinbase)/self.unitsize(unit)
	
	def unitsize(self, unit):
		"""
		unitsize returns the amount of time for one year related to a unit and
		to this daycount rule.
		"""
		return self._unitsize[unit]
	
	def timefactor(self, period):
		"""
		Returns an year fraction regarding period definition.
		This function always returns year's fraction.
		"""
		days = period.size() * self.daysinunit(period.unit)
		return float(days)/self.daysinbase
	
	def timefreq(self, period, frequency):
		"""
		timefreq returns the amount of time contained into the period adjusted 
		to the given frequency.
		"""
		tf = self.timefactor(period)
		return tf * self.unitsize(FREQ_MAP[frequency])


class Calendar(object):
	"""docstring for Calendar"""
	def __init__(self, cal):
		if not cal.startswith('cal'):
			raise Exception('Invalid calendar specification')
		name = cal.replace('cal', '')
		fname = name + '.cal'
		if not os.path.exists(fname):
			raise Exception('Invalid calendar specification: file not found')
		self._cal_spec = cal
		f = open(fname)
		self.holidays = [datetime.strptime(dt.strip(), '%Y-%m-%d').date() \
			for dt in f if not dt.strip() is '']
		f.close()
		self.startdate = date(self.holidays[0].year, 1, 1)
		self.enddate = date(self.holidays[-1].year, 12, 31)
		
		self.index = {}
		d1 = timedelta(1)
		dt = self.startdate
		w = c = 1
		while dt <= self.enddate:
			is_hol = dt in self.holidays or dt.weekday() in (5, 6)
			self.index[dt] = (w, c, is_hol)
			c += 1
			if not is_hol:
				w += 1
			dt += d1
	
	def workdays(self, dates):
		d1, d2 = dates
		d1 = datetime.strptime(d1, '%Y-%m-%d').date()
		d2 = datetime.strptime(d2, '%Y-%m-%d').date()
		return self.index[d2][0] - self.index[d1][0]
	
	def currentdays(self, dates):
		d1, d2 = dates
		d1 = datetime.strptime(d1, '%Y-%m-%d').date()
		d2 = datetime.strptime(d2, '%Y-%m-%d').date()
		return self.index[d2][1] - self.index[d1][1]
	
	def isworkday(self, dt):
		dt = datetime.strptime(dt, '%Y-%m-%d').date()
		return not self.index[dt][2]


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


# rate = '6%% annual simple (actual/365 Fixed)'
# rate = '0.09 annual compounded business/252 calANBIMA'
# rate = '0.06 annual continuous 30/360'

class InterestRate(object):
	"""
	InterestRate class
	
	This class receives a calendar instance in its constructor's parameter list
	because in some cases it's fairly common to user provide that information.
	Despite of having a default calendar set either into the system or for a given
	market, we are likely to handle the situation where interest rate has its own
	calendar and that calendar must be used to discount the cashflows.
	"""
	def __init__(self, rate, frequency, compounding, daycount, calendar=None):
		self.rate = rate
		self.frequency = frequency
		self.daycount = daycount
		self.compounding = compounding
		self._compoundingfunc = getattr(Compounding, self.compounding)
		self._daycount = DayCount(self.daycount)
		if calendar:
			self.calendar = Calendar(calendar)
		else:
			self.calendar = None
	
	def discount(self, period):
		"""Return the discount factor"""
		return 1.0/compound(period)
	
	def compound(self, period):
		"""Return the compounding factor"""
		if self.calendar:
			period = CalendarRangePeriod(period, self.calendar)
		
		t = self._daycount.timefreq(period, self.frequency)
		return self._compoundingfunc(self.rate, t)
	
	# write conversion functions: given other settings generate a different rate


