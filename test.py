#!/usr/local/bin/python
# encoding: utf-8

import math
import unittest
from datetime import date
from fixedincome import *

class TestPeriod(unittest.TestCase):
	def setUp(self):
		pass
	
	def testPeriod(self):
		"""testPeriod: test for fixed period"""
		p = Period('1 month')
		self.assertEqual(p.size(), 1.0)
		self.assertEqual(p.unit, 'month')
		
		p = Period('2.5 months')
		self.assertEqual(p.size(), 2.5)
		self.assertEqual(p.unit, 'month')
		
		p = Period('22.55 months')
		self.assertEqual(p.size(), 22.55)
		self.assertEqual(p.unit, 'month')
		
		p = Period('1.5 years')
		self.assertEqual(p.size(), 1.5)
		self.assertEqual(p.unit, 'year')
		
		p = Period('1.5 quarters')
		self.assertEqual(p.size(), 1.5)
		self.assertEqual(p.unit, 'quarter')
	
		p = Period('15 days')
		self.assertEqual(p.size(), 15)
		self.assertEqual(p.unit, 'day')
	
	def testPeriodError(self):
		"""testPeriodError: test for error in period specification"""
		with self.assertRaises(Exception):
			p = Period('1 monthss')

	def testTimeInterval(self):
		"""docstring for testTimeInterval"""
		p = Period('2012-07-12:2012-07-16')
		self.assertEqual(p.size(), 4)
		self.assertEqual(p.unit, 'day')
	
	def testTimeIntervalWithDate(self):
		"""docstring for testTimeIntervalWithDate"""
		p = Period( ("2012-7-12","2012-7-22") )
		self.assertEqual(p.size(), 10)
		self.assertEqual(p.unit, 'day')
	
	def testTimeIntervalError(self):
		"""docstring for testTimeInterval"""
		with self.assertRaises(Exception):
			p = Period('2012-12-12:2012-10-16')

	def testTimeIntervalErrorWithDate(self):
		"""docstring for testTimeInterval"""
		d1 = "2012-07-12"
		d2 = "2012-07-27" # 15 days
		with self.assertRaises(Exception):
			p = Period((d2,d1))
		p = Period('2012-07-12:2012-07-22')
		self.assertEqual(p.size(), 10)
		self.assertEqual(p.unit, 'day')
		p = Period('15 days')
		self.assertEqual(p.size(), 15)
		self.assertEqual(p.unit, 'day')
		

class TestDayCount(unittest.TestCase):
	def setUp(self):
		pass
	
	def testDayCount(self):
		"""Testing day count rules"""
		dc = DayCount('actual/365 Fixed')
		self.assertEqual(dc.unitsize('day'), 365)
		# ---
		p = Period('1 year')
		self.assertEqual(p.timefactor(dc), 1)
		# ---
		p = Period('1 half-year')
		self.assertEqual(p.timefactor(dc), 1.0/2)
		# ---
		p = Period('1 quarter')
		self.assertEqual(p.timefactor(dc), 1.0/4)
		# ---
		p = Period('1 month')
		self.assertEqual(round(p.timefactor(dc), 6), round(1.0/12, 6))
		# ---
		p = Period('1 day')
		self.assertEqual(p.timefactor(dc), 1.0/dc.daysinbase)
		# +++
		dc = DayCount('business/252')
		self.assertEqual(dc.unitsize('day'), 252)
		p = Period('2012-07-12:2012-10-16')
		self.assertEqual(p.timefactor(dc), 96.0/252)
		# ---
		p = Period('1 year')
		self.assertEqual(p.timefactor(dc), 1)
		# ---
		p = Period('1 half-year')
		self.assertEqual(p.timefactor(dc), 1.0/2)
		# ---
		p = Period('1 quarter')
		self.assertEqual(p.timefactor(dc), 1.0/4)
		# ---
		p = Period('1 month')
		self.assertEqual(round(p.timefactor(dc), 6), round(1.0/12, 6))
		# ---
		p = Period('1 day')
		self.assertEqual(p.timefactor(dc), 1.0/dc.daysinbase)
	
	def testActual360(self):
		"""docstring for testActual360"""
		dc = DayCount('actual/360')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinunit('month'), 30)
		self.assertEqual(dc.daysinunit('quarter'), 90)
		self.assertEqual(dc.daysinunit('half-year'), 180)
		self.assertEqual(dc.daysinbase, 360)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
		
		p = Period('2012-07-12:2012-07-16')
		self.assertEqual(p.timefactor(dc), 4.0/360)
		p = Period('2012-07-12:2012-07-22')
		self.assertEqual(p.timefactor(dc), 10.0/360)
		
	def testBusiness252(self):
		"""docstring for testBusiness252"""
		dc = DayCount('business/252')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinunit('month'), 21)
		self.assertEqual(dc.daysinunit('quarter'), 63)
		self.assertEqual(dc.daysinunit('half-year'), 126)
		self.assertEqual(dc.daysinunit('year'), 252)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
		self.assertEqual(dc.daysinbase, 252)
		
	def testActual365(self):
		"""docstring for testActual365"""
		dc = DayCount('actual/365 Fixed')
		self.assertEqual(dc.daysinunit('day'), 1)
		self.assertEqual(dc.daysinbase, 365)
		self.assertEqual(dc.daysinunit('year'), dc.daysinbase)
		self.assertEqual(dc.unitsize('day'), dc.daysinbase)
		
		p = Period('2012-07-12:2012-07-16')
		self.assertEqual(p.timefactor(dc), 4.0/365)
		p = Period('2012-07-12:2012-07-22')
		self.assertEqual(p.timefactor(dc), 10.0/365)


class TestCompounding(unittest.TestCase):
	def setUp(self):
		pass
	
	def testSimpleCompounding(self):
		"""docstring for testSimpleCompounding"""
		smp = Compounding.simple
		self.assertEqual(1 + 0.5*2, smp(0.5, 2))

	def testCompoundedCompounding(self):
		"""docstring for testCompoundedCompounding"""
		disc = Compounding.compounded
		self.assertEqual((1 + 0.5)**2, disc(0.5, 2))
	
	def testContinuousCompounding(self):
		"""docstring for testContinuousCompounding"""
		cont = Compounding.continuous
		self.assertEqual(math.exp(0.5*2), cont(0.5, 2))
	

class TestInterestRate(unittest.TestCase):
	def setUp(self):
		pass
	
	def testInterestRateDefault(self):
		"""Testing InterestRate initialization"""
		ir = InterestRate(0.1, 'annual', 'simple', 'actual/360')
		smp = Compounding.simple
		self.assertEqual(ir.compound(Period('1 month')), smp(0.1, 1.0/12))
		self.assertEqual(ir.compound('1 month'), smp(0.1, 1.0/12))
		self.assertEqual(ir.compound('2012-07-12:2012-07-22'), smp(0.1, 10.0/360))
		p = Period( ("2012-7-12", "2012-7-22") )
		self.assertEqual(ir.compound(p), smp(0.1, 10.0/360))
	
	def testInterestRateFrequency(self):
		"""docstring for testInterestRateFrequency"""
		smp = Compounding.simple
		ir = InterestRate(0.1, 'monthly', 'simple', 'actual/360')
		self.assertEqual(ir.compound('1 month'), smp(0.1, 1.0))
		ir = InterestRate(0.1, 'semi-annual', 'simple', 'actual/360')
		self.assertEqual(ir.compound('1 month'), smp(0.1, 1.0/6))
		ir = InterestRate(0.1, 'daily', 'simple', 'actual/360')
		self.assertEqual(ir.compound('1 month'), smp(0.1, 30))
	
	def testInterestRateCompounding(self):
		"""docstring for testInterestRateCompounding"""
		func = Compounding.compounded
		ir = InterestRate(0.1, 'annual', 'compounded', 'actual/360')
		self.assertEqual(ir.compound('1 month'), func(0.1, 1.0/12))
		ir = InterestRate(0.1, 'semi-annual', 'compounded', 'actual/360')
		self.assertEqual(ir.compound('1 month'), func(0.1, 1.0/6))
		ir = InterestRate(0.1, 'daily', 'compounded', 'actual/360')
		self.assertEqual(ir.compound('1 month'), func(0.1, 30))
	

class TestCalendar(unittest.TestCase):
	def setUp(self):
		pass

	def testCalendarInstanciation(self):
		cal = Calendar(holidays="holidays.txt")
		days = cal.days_between('2012-10-21', '2015-10-21')
		self.assertEqual(754, days, 'Wrong business days amount')

if __name__ == '__main__':
	unittest.main(verbosity=2)
