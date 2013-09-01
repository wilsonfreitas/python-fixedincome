#!/usr/local/bin/python
# encoding: utf-8

import math
import unittest
from datetime import date
from fixedincome import *


class TestPeriod(unittest.TestCase):
	def test_GenericPeriod(self):
		p = GenericPeriod('day')
		with self.assertRaises(Exception):
			p.size()
	
	def test_Period__str__(self):
		p = period('1 month')
		self.assertEqual(str(p), '1.0 month')
		p = period('1.5 month')
		self.assertEqual(str(p), '1.5 months')
		p = period('1.25 month')
		self.assertEqual(str(p), '1.2 months')
	
	def test_FixedTimePeriod(self):
		'FixedTimePeriod creation'
		p = period('1 month')
		self.assertEqual(type(p), FixedTimePeriod)
		self.assertEqual(p.size(), 1.0)
		self.assertEqual(p.unit, 'month')
		
		p = period('1.5 years')
		self.assertEqual(type(p), FixedTimePeriod)
		self.assertEqual(p.size(), 1.5)
		self.assertEqual(p.unit, 'year')
		
		p = period('1.5 quarters')
		self.assertEqual(type(p), FixedTimePeriod)
		self.assertEqual(p.size(), 1.5)
		self.assertEqual(p.unit, 'quarter')
		
		with self.assertRaises(Exception):
			p = period('1 monthss')
	
	def test_DateRangePeriod(self):
		'DateRangePeriod creation'
		p = period('2012-07-12:2012-07-16')
		self.assertEqual(p.size(), 4)
		self.assertEqual(p.unit, 'day')
		
		with self.assertRaises(Exception):
			p = period('2012-12-12:2012-10-16')
	
	def test_CalendarRangePeriod(self):
		'CalendarRangePeriod instanciation'
		p = period('2002-07-12:2002-07-22')
		cal = Calendar('Test')
		c = CalendarRangePeriod(p, cal)
		self.assertEqual(p.dates, c.dates)
		self.assertEqual(c.calendar, cal)
		self.assertEqual(cal.workdays(('2002-07-12', '2002-07-22')), c.size())


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
		
	def test_Calendar_big_calendar_load_and_workdays(self):
		'loading a big calendar and computing workdays between 2 dates'
		cal = Calendar('ANBIMA')
		days = cal.workdays(('2002-01-01', '2002-01-02'))
		self.assertEqual(0, days, 'Wrong business days amount')
		self.assertEqual(cal.workdays(('2013-01-01', '2013-01-31')), 21)
		self.assertEqual(cal.workdays(('2013-01-01', '2014-01-01')), 252)
		self.assertEqual(cal.workdays(('2014-01-01', '2015-01-01')), 252)
		self.assertEqual(cal.workdays(('2013-08-21', '2013-08-24')), 2)
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
	
	def test_Calendar_next_workday(self):
		"""next_workday calculations"""
		cal = Calendar('Test')
		self.assertEqual(cal.adjust_next('2001-01-01'), '2001-01-02')
		
	def test_Calendar_previous_workday(self):
		"""previous_workday calculations"""
		cal = Calendar('Test')
		self.assertEqual(cal.adjust_previous('2001-08-12'), '2001-08-10')
		


class TestCompounding(unittest.TestCase):
	def test_names(self):
		'Compounding names'
		u = ('compounded', 'continuous', 'simple')
		t = tuple(sorted(u))
		self.assertEqual( t, tuple(sorted(Compounding.names)) )
	
	def test_Compounding(self):
		'Compounding instanciation'
		comp = Compounding('simple')
		self.assertEqual(comp.name, 'simple')
		
		with self.assertRaises(Exception):
			Compounding('blah')
		
		with self.assertRaises(AttributeError):
			comp.name = 'new'

	def testSimpleCompounding(self):
		'Compounding simple compounding'
		smp = Compounding.simple
		self.assertEqual(1 + 0.5*2, smp(0.5, 2))

	def testCompoundedCompounding(self):
		'Compounding discrete (compounded) compounding'
		disc = Compounding.compounded
		self.assertEqual((1 + 0.5)**2, disc(0.5, 2))
	
	def testContinuousCompounding(self):
		'Compounding continuous compounding'
		cont = Compounding.continuous
		self.assertEqual(math.exp(0.5*2), cont(0.5, 2))


class TestTimeUnit(unittest.TestCase):
	def test_names(self):
		'TimeUnit names'
		u = ('year', 'half-year', 'quarter', 'month', 'day')
		t = tuple(sorted(u))
		self.assertEqual( t, tuple(sorted(TimeUnit.names)) )


class TestFrequency(unittest.TestCase):
	def test_Frequency(self):
		"""Frequency instanciation"""
		f = Frequency('annual')
		self.assertEqual(f.name, 'annual')
		self.assertEqual(f, Frequency('annual'))
		
		with self.assertRaises(AttributeError):
			f.name = 'annu'
		with self.assertRaises(Exception):
			Frequency('annu')
		
	def test_names(self):
		'Frequency names'
		u = ('annual', 'daily', 'monthly', 'quarterly', 'semi-annual')
		t = tuple(sorted(u))
		self.assertEqual( t, tuple(sorted(Frequency.names)) )
	
	def test_Frequency_unit(self):
		'Frequency unit'
		f = Frequency('annual')
		self.assertEqual(f.unit(), 'year')


class TestDayCount(unittest.TestCase):
	def test_DayCount(self):
		'DayCount instanciation'
		dc = DayCount('business/252')
		self.assertEqual(dc, DayCount('business/252'))
		self.assertNotEqual(dc, DayCount('actual/365'))
		self.assertEqual(dc.name, 'business/252')
		with self.assertRaises(AttributeError):
			dc.name = 'test'
		
		self.assertEqual( ('actual/360', '30E+/360', 'actual/364', 'actual/365',
			'30/360', 'business/252', 'actual/365L', '30E/360 ISDA',
			'30/360 US'), DayCount.names)
	
	def test_names(self):
		'DayCount names'
		u = ('actual/360', '30E+/360', 'actual/364', 'actual/365',
			'30/360', 'business/252', 'actual/365L', '30E/360 ISDA',
			'30/360 US')
		t = tuple(sorted(u))
		self.assertEqual( t, tuple(sorted(DayCount.names)) )

	def testBusiness252(self):
		'DayCount business/252'
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
		'DayCount actual/360'
		dc = DayCount('actual/360')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinunit('month'), 30)
		self.assertEqual(dc.daysinunit('quarter'), 90)
		self.assertEqual(dc.daysinunit('half-year'), 180)
		self.assertEqual(dc.daysinbase, 360)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
	
	def test_Actual360_timefactor(self):
		'DayCount actual/360 timefactor'
		dc = DayCount('actual/360')
		p = period('2012-07-12:2012-07-16')
		self.assertEqual(dc.timefactor(p), 4.0/dc.daysinbase)
		p = period('2012-07-12:2012-07-22')
		self.assertEqual(dc.timefactor(p), 10.0/dc.daysinbase)
		
	def test_Actual360_timefreq(self):
		'DayCount actual/360 timefreq'
		dc = DayCount('actual/360')
		p = period('2012-07-12:2012-07-16')
		self.assertAlmostEqual(dc.timefreq(p, Frequency('annual')), 4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('semi-annual')), 2*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('quarterly')), 4*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('monthly')), 12*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('daily')), 4.0)
		# p = period('2012-07-12:2012-07-22')
		# self.assertEqual(dc.timefactor(p), 10.0/360)
		
	def testActual365(self):
		'DayCount actual/365'
		dc = DayCount('actual/365')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinbase, 365)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
	
	def test_Actual365_timefactor(self):
		'DayCount actual/365 timefactor'
		dc = DayCount('actual/365')
		p = period('2012-07-12:2012-07-16')
		self.assertEqual(dc.timefactor(p), 4.0/dc.daysinbase)
		p = period('2012-07-12:2012-07-22')
		self.assertEqual(dc.timefactor(p), 10.0/dc.daysinbase)
	
	def test_Actual365_timefreq(self):
		'DayCount actual/365 timefreq'
		dc = DayCount('actual/365')
		p = period('2012-07-12:2012-07-16')
		self.assertAlmostEqual(dc.timefreq(p, Frequency('annual')), 4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('semi-annual')), 2*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('quarterly')), 4*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('monthly')), 12*4.0/dc.daysinbase)
		self.assertAlmostEqual(dc.timefreq(p, Frequency('daily')), 4.0)
	
	def test_timefactor_FixedPeriod(self):
		'DayCount timefactor for FixedTimePeriod'
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
	
	def test_Daycount_period_conversions(self):
		'DayCount period conversions'
		dc = DayCount('actual/365')
		p = period('1 year')
		self.assertEqual(p.size()*365, dc.day(p))
		self.assertEqual(p.size()*12, dc.month(p))
		self.assertEqual(p.size()*4, dc.quarter(p))
		self.assertEqual(p.size()*2, dc.half_year(p))
		self.assertEqual(p.size(), dc.year(p))
		p = period('1 half-year')
		self.assertEqual(p.size()*365/2.0, dc.in_unit(p, 'day'))
		self.assertEqual(p.size()*6, dc.in_unit(p, 'month'))
		self.assertEqual(p.size()*2, dc.in_unit(p, 'quarter'))
		self.assertEqual(p.size()*1, dc.in_unit(p, 'half-year'))
		self.assertEqual(p.size()*0.5, dc.in_unit(p, 'year'))
		p = period('1 quarter')
		self.assertEqual(p.size()*365/4.0, dc.in_unit(p, 'day'))
		self.assertEqual(p.size()*3, dc.in_unit(p, 'month'))
		self.assertEqual(p.size()*1, dc.in_unit(p, 'quarter'))
		self.assertEqual(p.size()*0.5, dc.in_unit(p, 'half-year'))
		self.assertEqual(p.size()*1.0/4, dc.in_unit(p, 'year'))
		p = period('1 month')
		self.assertEqual(p.size()*365/12.0, dc.in_unit(p, 'day'))
		self.assertEqual(p.size()*1, dc.in_unit(p, 'month'))
		self.assertEqual(p.size()*3, dc.in_unit(p, 'quarter'))
		self.assertEqual(p.size()*6, dc.in_unit(p, 'half-year'))
		self.assertEqual(p.size()*12, dc.in_unit(p, 'year'))
		p = period('1 day')
		self.assertEqual(p.size(), dc.in_unit(p, 'day'))
		self.assertEqual(p.size()*12/365.0, dc.in_unit(p, 'month'))
		self.assertEqual(p.size()* 4/365.0, dc.in_unit(p, 'quarter'))
		self.assertEqual(p.size()* 2/365.0, dc.in_unit(p, 'half-year'))
		self.assertEqual(p.size()* 1/365.0, dc.in_unit(p, 'year'))


class TestInterestRate(unittest.TestCase):
	def test_InterestRate(self):
		'InterestRate instanciation'
		ir = InterestRate(0.1, Frequency('annual'), Compounding('simple'), 
			DayCount('actual/360'))
		self.assertEqual(ir.rate, 0.1)
		self.assertEqual(ir.frequency, Frequency('annual'))
		self.assertEqual(ir.compounding, Compounding('simple'))
		self.assertEqual(ir.daycount, DayCount('actual/360'))
		self.assertEqual(ir.calendar, None)
		
		ir = InterestRate(0.1, Frequency('annual'), Compounding('simple'), 
			DayCount('business/252'), Calendar('Test'))
		self.assertEqual(ir.rate, 0.1)
		self.assertEqual(ir.frequency, Frequency('annual'))
		self.assertEqual(ir.compounding, Compounding('simple'))
		self.assertEqual(ir.daycount, DayCount('business/252'))
		self.assertEqual(ir.calendar, Calendar('Test'))
	
	def test_InterestRate_compound(self):
		'InterestRate compound'
		ir = InterestRate(0.1, Frequency('annual'), Compounding('simple'), 
			DayCount('actual/360'))
		smp = Compounding.simple
		self.assertEqual(ir.compound(period('1 month')), smp(0.1, 1.0/12))
		p = period("2012-7-12:2012-7-22")
		self.assertEqual(ir.compound(p), smp(0.1, 10.0/360))
	
	def test_InterestRate_simple_rate(self):
		'InterestRate simple rate'
		comp = Compounding("simple")
		ir = InterestRate(0.1, Frequency('annual'), comp, 
			DayCount('business/252'), Calendar('Test'))
		smp = Compounding.simple
		comp_val = smp(0.1, 6.0/252)
		
		p = period("2002-7-12:2002-7-22")
		comp = ir.compound(p)
		self.assertEqual(comp, comp_val)
	
	def test_InterestRate_simple_rate_2(self):
		'InterestRate with DayCount different from business defining Calendar'
		comp = Compounding("simple")
		cal = Calendar('Test')
		freq = Frequency('annual')
		dc = DayCount('actual/365')
		with self.assertRaises(Exception):
			InterestRate(0.1, freq, comp, dc, cal)
	
	def test_InterestRate_compounding_rate(self):
		'InterestRate compound rate'
		func = Compounding.compounded
		comp = Compounding('compounded')
		p = period('1 month')
		dc = DayCount('actual/360')
		
		ir = InterestRate(0.1, Frequency('annual'), comp, dc)
		self.assertEqual(ir.compound(p), func(0.1, 1.0/12))
		
		ir = InterestRate(0.1, Frequency('semi-annual'), comp, dc)
		self.assertEqual(ir.compound(p), func(0.1, 1.0/6))
		
		ir = InterestRate(0.1, Frequency('daily'), comp, dc)
		self.assertEqual(ir.compound(p), func(0.1, 30))
		
	def test_ir(self):
		"""ir function"""
		ir_ = ir('0.06 annual simple actual/365')
		self.assertEqual(ir_.rate, 0.06)
		self.assertEqual(ir_.compounding, Compounding('simple'))
		self.assertEqual(ir_.frequency, Frequency('annual'))
		self.assertEqual(ir_.daycount, DayCount('actual/365'))
		
		ir_ = ir('0.01 semi-annual compounded business/252 calTest')
		self.assertEqual(ir_.rate, 0.01)
		self.assertEqual(ir_.compounding, Compounding('compounded'))
		self.assertEqual(ir_.frequency, Frequency('semi-annual'))
		self.assertEqual(ir_.daycount, DayCount('business/252'))
		self.assertEqual(ir_.calendar, Calendar('Test'))
		
		with self.assertRaises(Exception):
			ir('0.01 semi-annual compounded actual/365 calTest')
	

if __name__ == '__main__':
	unittest.main(verbosity=2)
