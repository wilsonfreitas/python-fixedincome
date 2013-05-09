#!/usr/local/bin/python
# encoding: utf-8

import math
import unittest
from datetime import date
from fixedincome import *


class TestTimeUnit(unittest.TestCase):
	def test_names(self):
		u = ('year', 'half-year', 'quarter', 'month', 'day')
		t = tuple(sorted(u))
		self.assertEqual( t, tuple(sorted(TimeUnit.names)) )

class TestFrequency(unittest.TestCase):
	def test_names(self):
		u = ('annual', 'daily', 'monthly', 'quarterly', 'semi-annual')
		t = tuple(sorted(u))
		self.assertEqual( t, tuple(sorted(Frequency.names)) )

class TestCompounding(unittest.TestCase):
	def test_names(self):
		u = ('compounded', 'continuous', 'simple')
		t = tuple(sorted(u))
		self.assertEqual( t, tuple(sorted(Compounding.names)) )

class TestPeriod(unittest.TestCase):
	def testFixedPeriod(self):
		p = period('1 month')
		self.assertEqual(p.size(), 1.0)
		self.assertEqual(p.unit, 'month')
		
		p = period('2.5 months')
		self.assertEqual(p.size(), 2.5)
		self.assertEqual(p.unit, 'month')
		
		p = period('22.55 months')
		self.assertEqual(p.size(), 22.55)
		self.assertEqual(p.unit, 'month')
		
		p = period('1.5 years')
		self.assertEqual(p.size(), 1.5)
		self.assertEqual(p.unit, 'year')
		
		p = period('1.5 quarters')
		self.assertEqual(p.size(), 1.5)
		self.assertEqual(p.unit, 'quarter')
	
		p = period('15 days')
		self.assertEqual(p.size(), 15)
		self.assertEqual(p.unit, 'day')
	
	def testPeriodError(self):
		with self.assertRaises(Exception):
			p = period('1 monthss')

	def testTimeInterval(self):
		p = period('2012-07-12:2012-07-16')
		self.assertEqual(p.size(), 4)
		self.assertEqual(p.unit, 'day')
	
	def testTimeIntervalError(self):
		with self.assertRaises(Exception):
			p = period('2012-12-12:2012-10-16')

	def testTimeIntervalErrorWithDate(self):
		d1 = "2012-07-12"
		d2 = "2012-07-27" # 15 days
		with self.assertRaises(Exception):
			p = period((d2,d1))
		p = period('2012-07-12:2012-07-22')
		self.assertEqual(p.size(), 10)
		self.assertEqual(p.unit, 'day')
		p = period('15 days')
		self.assertEqual(p.size(), 15)
		self.assertEqual(p.unit, 'day')
	
	def test_CalendarRangePeriod(self):
		p = period('2002-07-12:2002-07-22')
		cal = Calendar('Test')
		c = CalendarRangePeriod(p, cal)
		self.assertEqual(p.dates, c.dates)
		self.assertEqual(c.calendar, cal)
		self.assertEqual(cal.workdays(('2002-07-12', '2002-07-22')), c.size())

class TestDayCount(unittest.TestCase):
	def test_DayCount(self):
		dc = DayCount('business/252')
		self.assertEqual(dc, DayCount('business/252'))
		self.assertNotEqual(dc, DayCount('actual/365'))
		
		self.assertEqual( ('actual/360', '30E+/360', 'actual/364', 'actual/365',
			'30/360', 'business/252', 'actual/365L', '30E/360 ISDA',
			'30/360 US'), DayCount.names)
		self.assertEqual( ('quarterly', 'semi-annual', 'annual', 'daily', 
			'monthly'), Frequency.names)
	
	def testBusiness252(self):
		dc = DayCount('business/252')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinunit('month'), 21)
		self.assertEqual(dc.daysinunit('quarter'), 63)
		self.assertEqual(dc.daysinunit('half-year'), 126)
		self.assertEqual(dc.daysinunit('year'), 252)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
		self.assertEqual(dc.daysinbase, 252)
		
	def testActual360(self):
		dc = DayCount('actual/360')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinunit('month'), 30)
		self.assertEqual(dc.daysinunit('quarter'), 90)
		self.assertEqual(dc.daysinunit('half-year'), 180)
		self.assertEqual(dc.daysinbase, 360)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
	
	def test_Actual360_timefactor(self):
		dc = DayCount('actual/360')
		p = period('2012-07-12:2012-07-16')
		self.assertEqual(dc.timefactor(p), 4.0/dc.daysinbase)
		p = period('2012-07-12:2012-07-22')
		self.assertEqual(dc.timefactor(p), 10.0/dc.daysinbase)
		
	def test_Actual360_timefreq(self):
		dc = DayCount('actual/360')
		p = period('2012-07-12:2012-07-16')
		self.assertAlmostEqual(dc.timefreq(p, 'annual'), 4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'semi-annual'), 2*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'quarterly'), 4*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'monthly'), 12*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'daily'), 4.0)
		# p = period('2012-07-12:2012-07-22')
		# self.assertEqual(dc.timefactor(p), 10.0/360)
		
	def testActual365(self):
		dc = DayCount('actual/365')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinbase, 365)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
	
	def test_Actual365_timefactor(self):
		dc = DayCount('actual/365')
		p = period('2012-07-12:2012-07-16')
		self.assertEqual(dc.timefactor(p), 4.0/dc.daysinbase)
		p = period('2012-07-12:2012-07-22')
		self.assertEqual(dc.timefactor(p), 10.0/dc.daysinbase)
	
	def test_Actual365_timefreq(self):
		dc = DayCount('actual/365')
		p = period('2012-07-12:2012-07-16')
		self.assertAlmostEqual(dc.timefreq(p, 'annual'), 4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'semi-annual'), 2*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'quarterly'), 4*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'monthly'), 12*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, 'daily'), 4.0)
	
	def test_timefactor_FixedPeriod(self):
		dc = DayCount('actual/365')
		p = period('1 year')
		self.assertEqual(dc.timefactor(p), 1)
		p = period('1 half-year')
		self.assertEqual(dc.timefactor(p), 1.0/2)
		p = period('1 quarter')
		self.assertEqual(dc.timefactor(p), 1.0/4)
		p = period('1 month')
		self.assertEqual(round(dc.timefactor(p), 6), round(1.0/12, 6))
		p = period('1 day')
		self.assertEqual(dc.timefactor(p), 1.0/dc.daysinbase)
		
		dc = DayCount('business/252')
		p = period('1 year')
		self.assertEqual(dc.timefactor(p), 1)
		p = period('1 half-year')
		self.assertEqual(dc.timefactor(p), 1.0/2)
		p = period('1 quarter')
		self.assertEqual(dc.timefactor(p), 1.0/4)
		p = period('1 month')
		self.assertEqual(round(dc.timefactor(p), 6), round(1.0/12, 6))
		p = period('1 day')
		self.assertEqual(dc.timefactor(p), 1.0/dc.daysinbase)


class TestCompounding(unittest.TestCase):
	def testSimpleCompounding(self):
		smp = Compounding.simple
		self.assertEqual(1 + 0.5*2, smp(0.5, 2))

	def testCompoundedCompounding(self):
		disc = Compounding.compounded
		self.assertEqual((1 + 0.5)**2, disc(0.5, 2))
	
	def testContinuousCompounding(self):
		cont = Compounding.continuous
		self.assertEqual(math.exp(0.5*2), cont(0.5, 2))
	

class TestInterestRate(unittest.TestCase):
	def testInterestRateDefault(self):
		ir = InterestRate(0.1, 'annual', 'simple', 'actual/360')
		smp = Compounding.simple
		self.assertEqual(ir.compound(period('1 month')), smp(0.1, 1.0/12))
		self.assertEqual(ir.compound('1 month'), smp(0.1, 1.0/12))
		self.assertEqual(ir.compound('2012-07-12:2012-07-22'), smp(0.1, 10.0/360))
		p = period( ("2012-7-12", "2012-7-22") )
		self.assertEqual(ir.compound(p), smp(0.1, 10.0/360))
	
	def testInterestRateDefault(self):
		ir = InterestRate(0.1, 'annual', 'simple', 'business/252', calendar='Test')
		smp = Compounding.simple
		comp_val = smp(0.1, 6.0/252)
		
		p = period("2002-7-12:2002-7-22")
		comp = ir.compound(p)
		self.assertEqual(comp, comp_val)
	
	def testInterestRateFrequency(self):
		smp = Compounding.simple
		p = period('1 month')
		
		ir = InterestRate(0.1, 'monthly', 'simple', 'actual/360')
		self.assertEqual(ir.compound(p), smp(0.1, 1.0))
		
		ir = InterestRate(0.1, 'semi-annual', 'simple', 'actual/360')
		self.assertEqual(ir.compound(p), smp(0.1, 1.0/6))
		
		ir = InterestRate(0.1, 'daily', 'simple', 'actual/360')
		self.assertEqual(ir.compound(p), smp(0.1, 30))
	
	def testInterestRateCompounding(self):
		func = Compounding.compounded
		p = period('1 month')
		
		ir = InterestRate(0.1, 'annual', 'compounded', 'actual/360')
		self.assertEqual(ir.compound(p), func(0.1, 1.0/12))
		
		ir = InterestRate(0.1, 'semi-annual', 'compounded', 'actual/360')
		self.assertEqual(ir.compound(p), func(0.1, 1.0/6))
		
		ir = InterestRate(0.1, 'daily', 'compounded', 'actual/360')
		self.assertEqual(ir.compound(p), func(0.1, 30))
		
	def test_ir(self):
		"""ir function"""
		ir_ = ir('0.06 annual simple actual/365')
		self.assertEqual(ir_.rate, 0.06)
		self.assertEqual(ir_.compounding, 'simple')
		self.assertEqual(ir_.frequency, 'annual')
		self.assertEqual(ir_.daycount, DayCount('actual/365'))
	

class TestCalendar(unittest.TestCase):
	def testCalendar(self):
		'calendar instanciation'
		with self.assertRaises(Exception):
			Calendar('AAA')
		with self.assertRaises(Exception):
			Calendar('calAAA')
		cal = Calendar('Test')
		self.assertEqual(cal, Calendar('Test'))
		self.assertEqual(cal.startdate.isoformat(), '2001-01-01')
		self.assertEqual(cal.enddate.isoformat(), '2002-12-31')
		self.assertEqual(len(cal.holidays), 2)
		self.assertEqual(date(2001, 1, 1) in cal.holidays, True)
		self.assertEqual(cal.index[cal.startdate], (1, 1, True))
		self.assertEqual(cal.index[cal.enddate], (520, 730, False))
	
	def test_Calendar_workdays(self):
		'calendar count of workdays'
		cal = Calendar('Test')
		days = cal.workdays(('2002-01-01', '2002-01-02'))
		self.assertEqual(0, days, 'Wrong business days amount')
		self.assertEqual(cal.workdays(('2002-07-12', '2002-07-22')), 6)
	
	def test_Calendar_currentdays(self):
		'calendar count of currentdays'
		cal = Calendar('Test')
		days = cal.currentdays(('2002-01-01', '2002-01-02'))
		self.assertEqual(1, days, 'Wrong current days amount')
	
	def test_Calendar_isworkday(self):
		'calendar count of currentdays'
		cal = Calendar('Test')
		self.assertEqual(cal.isworkday('2002-01-01'), False) # New year
		self.assertEqual(cal.isworkday('2002-01-02'), True)  # First workday
		self.assertEqual(cal.isworkday('2002-01-05'), False) # Saturday

if __name__ == '__main__':
	unittest.main(verbosity=2)
