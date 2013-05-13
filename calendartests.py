
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
	if m == 6:
		return 2
	else:
		return 1

def weekendcount_sat(m):
	if m >= 1:
		return 2
	else:
		return 1

workdays_count = {
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
	d = (d2 - d1).days
	weeks = d/7
	mdays = d % 7
	wd = workdays_count[d1.weekday()](mdays)
	wdays = d - weeks*2 - wd
	if wdays < 0:
		return 0
	else:
		return wdays

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
	'sunday']

for weekday in weekdays:
	print '---', weekday
	for l in open('%s.csv' % weekday):
		d1, d2, wd = l.strip().split(',')
		print int(wd), workdays((d1, d2))
		assert int(wd) == workdays((d1, d2))



