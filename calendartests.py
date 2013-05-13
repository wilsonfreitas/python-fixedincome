
from datetime import datetime, date, timedelta

def weekendcount(e):
	def _weekendcount(m):
		if m == e:
			return 1
		elif m > e:
			return 2
		else:
			return 0
	return _weekendcount

def weekendcount_sun(m):
	return int(m == 6)*2 or 1

def weekendcount_sat(m):
	return int(m >= 1)*2 or 1

non_workdays_count = {
	0: weekendcount(5),
	1: weekendcount(4),
	2: weekendcount(3),
	3: weekendcount(2),
	4: weekendcount(1),
	5: weekendcount_sat,
	6: weekendcount_sun,
}

def workdays(dates):
	d1, d2 = dates
	d1 = datetime.strptime(d1, '%Y-%m-%d').date()
	d2 = datetime.strptime(d2, '%Y-%m-%d').date()
	cdays = (d2 - d1).days # current days between 2 dates
	weeks = d/7 # weeks
	rdays = d%7 # remaining days
	# computing the amount of non-working days to subtract
	wdays = d - non_workdays_count[d1.weekday()](rdays) + weeks*2
	return max(0, wdays)

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
	'sunday']

for weekday in weekdays:
	print '---', weekday
	for l in open('%s.csv' % weekday):
		d1, d2, wd = l.strip().split(',')
		print int(wd), workdays((d1, d2))
		assert int(wd) == workdays((d1, d2))



