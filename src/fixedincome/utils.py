"""Utility functions for fixed income calculations."""

import re
from datetime import datetime

import numpy as np
from bizdays import Calendar

from .core import (
    Compounding,
    DateRangePeriod,
    DayCount,
    FixedTimePeriod,
    Frequency,
    InterestRate,
    TimeUnit,
)


def ir(irspec):
    """
    Return a InterestRate object for a given interest rate specification.
    The interest rate specification is a string like:

    '0.06 annual simple actual/365'
    '0.09 annual compounded business/252 calANBIMA'
    '0.06 annual continuous 30/360'

    The specification must contain all information required to instanciate a
    InterestRate object. The InterestRate constructor requires:
    - rate
    - frequency
    - compounding
    - daycount
    and depending on which daycount is used the calendar must be set. Otherwise,
    it defaults to None.
    """
    calendar = None
    tokens = irspec.split()
    for tok in tokens:
        m = re.match(r"^(\d+)(\.\d+)?$", tok)
        if m:
            rate = float(m.group())
        elif tok in Compounding.names:
            compounding = Compounding(tok)
        elif tok in DayCount.names:
            daycount = DayCount(tok)
        elif tok in Frequency.names:
            frequency = Frequency(tok)
        elif tok.startswith("cal"):
            calendar = Calendar(tok.replace("cal", ""))
    return InterestRate(rate, frequency, compounding, daycount, calendar)


def compound(ir, period):
    """
    Return the compounding factor regarding an interst rate and a period.
    
    Supports vectorized operations with numpy arrays, pandas Series, and Polars Series.
    When the InterestRate has an array-like rate, the result will be a numpy array
    that can be directly assigned to DataFrame columns.
    """
    return ir.compound(period)


def discount(ir, period):
    """
    Return the discount factor regarding an interest rate and a period.
    
    Supports vectorized operations with numpy arrays, pandas Series, and Polars Series.
    When the InterestRate has an array-like rate, the result will be a numpy array
    that can be directly assigned to DataFrame columns.
    """
    return ir.discount(period)


def period(pspec):
    """
    Return a FixedTimePeriod or a DateRangePeriod instance, depending on the
    period specification string passed.

        # FixedTimePeriod
        p = period('15 days')
        p = period('1 month')
        p = period('2.5 months')
        p = period('22.55 months')
        p = period('1.5 years')
        p = period('1.5 quarters')

        # DateRangePeriod
        p = period('2012-07-12:2012-07-16')
        p = period('2012-07-12:2012-07-22')
    """
    w = "|".join(TimeUnit.names)
    m = re.match(r"^(\d+)(\.\d+)? (%s)s?$" % w, pspec)
    if m:
        istimerange = False
    elif len(pspec.split(":")) == 2:
        (start, end) = pspec.split(":")
        istimerange = True
    else:
        raise Exception("Invalid period specification")

    if istimerange:
        dates = (
            datetime.strptime(start, "%Y-%m-%d").date(),
            datetime.strptime(end, "%Y-%m-%d").date(),
        )
        return DateRangePeriod(dates, "day")
    else:
        g = m.groups()
        return FixedTimePeriod(float(g[0] + (g[1] or ".0")), g[2])


def periods(sizes, unit):
    """
    Create a FixedTimePeriod with vectorized sizes for batch calculations.
    
    Parameters
    ----------
    sizes : array-like
        Array of period sizes (can be numpy array, list, pandas Series, or Polars Series).
    unit : str
        Time unit ('year', 'month', 'day', 'quarter', 'half-year').
    
    Returns
    -------
    FixedTimePeriod
        A FixedTimePeriod object with array-based size for vectorized operations.
    
    Examples
    --------
    >>> import numpy as np
    >>> from fixedincome import periods
    >>> p = periods(np.array([1, 2, 3]), 'month')
    >>> p.size()
    array([1., 2., 3.])
    """
    return FixedTimePeriod(sizes, unit)


def rates(rates_array, frequency, compounding, daycount, calendar=None):
    """
    Create an InterestRate with vectorized rates for batch calculations.
    
    Parameters
    ----------
    rates_array : array-like
        Array of interest rates (can be numpy array, list, pandas Series, or Polars Series).
    frequency : Frequency or str
        Compounding frequency.
    compounding : Compounding or str
        Compounding type.
    daycount : DayCount or str
        Day count convention.
    calendar : Calendar, optional
        Calendar for business day calculations.
    
    Returns
    -------
    InterestRate
        An InterestRate object with array-based rate for vectorized operations.
    
    Examples
    --------
    >>> import numpy as np
    >>> from fixedincome import rates, Frequency, Compounding, DayCount
    >>> ir = rates(np.array([0.05, 0.06, 0.07]), 'annual', 'simple', 'actual/365')
    >>> ir.rate
    array([0.05, 0.06, 0.07])
    """
    # Convert string arguments to objects if needed
    if isinstance(frequency, str):
        frequency = Frequency(frequency)
    if isinstance(compounding, str):
        compounding = Compounding(compounding)
    if isinstance(daycount, str):
        daycount = DayCount(daycount)
    
    return InterestRate(rates_array, frequency, compounding, daycount, calendar)
