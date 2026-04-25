"""Utility functions for fixed income calculations."""

import re
from datetime import datetime

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
    """
    return ir.compound(period)


def discount(ir, period):
    """
    Return the discount factor regarding an interest rate and a period.
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
