"""
python-fixedincome is a small module focused on interest rate calculations.
It promotes an easy to use approach to set and handle the interest rate and its attributes:

* compounding factors
* day count rules
* compounding frequency
* calendar

This module also helps with interest rate conversions and computations of compounding
factors over time periods, using either business days and actual days.
"""

from .core import (
    CalendarRangePeriod,
    Compounding,
    DateRangePeriod,
    DayCount,
    FixedTimePeriod,
    Frequency,
    GenericPeriod,
    InterestRate,
    TimeUnit,
)
from .utils import compound, discount, ir, period

__version__ = "0.1.0"
__all__ = [
    "GenericPeriod",
    "FixedTimePeriod",
    "DateRangePeriod",
    "CalendarRangePeriod",
    "DayCount",
    "Frequency",
    "TimeUnit",
    "Compounding",
    "InterestRate",
    "ir",
    "compound",
    "discount",
    "period",
]
