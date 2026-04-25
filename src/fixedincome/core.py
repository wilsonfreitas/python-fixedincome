"""Core classes for fixed income calculations."""

import numpy as np


class GenericPeriod:
    """GenericPeriod class

    This class accommodates methods for time computing.
    """

    def __init__(self, unit):
        self.unit = unit

    def size(self):
        """docstring for numberof"""
        raise NotImplementedError(
            "The method numberof is not implemented for this "
            "class. User FixedTimePeriod or DateRangePeriod instead."
        )

    def __str__(self):
        return "%.1f %s%s" % (self.size(), self.unit, ("", "s")[self.size() > 1])


class FixedTimePeriod(GenericPeriod):
    """
    period('1 year')
    period('1 half-year')
    period('1 quarter')
    period('1 month')
    period('1 day')
    """

    def __init__(self, size, unit):
        super().__init__(unit)
        # Convert to numpy array for vectorization support
        self._size = np.asarray(size, dtype=np.float64)
        self._scalar_size = np.ndim(self._size) == 0

    def size(self):
        """Return the quantity related to the fixed period."""
        if self._scalar_size:
            return float(self._size)
        return self._size

    def __len__(self):
        return len(self._size) if not self._scalar_size else 1

    def __getitem__(self, idx):
        if self._scalar_size:
            if idx == 0 or idx == Ellipsis:
                return self._size.item()
            raise IndexError("index out of range")
        return self._size[idx]

    def __iter__(self):
        if self._scalar_size:
            yield self._size.item()
        else:
            yield from self._size.flat


class DateRangePeriod(GenericPeriod):
    """
    d1 = "2012-07-12"
    d2 = "2012-07-27"
    period((d1, d2))
    period('2012-07-12:2012-07-16')

    For now we can consider only the *day* time unit but we should be completely
    open to other time units such as *month* and *year* or even *quarter*.
    For example:
    period('2012-04:2012-12') -> from april, 2012 to december, 2012: 9 months
    period('2012:2012') -> from 2012 to 2012: 1 year
    period('2012-1:2012-3') -> from 2012 first quarter to 2012 third one: 3 quarters

    I still don't know how to handle that!

    This procedure includes starting and ending points.
    """

    def __init__(self, dates, unit="day"):
        super().__init__(unit)
        if dates[0] > dates[1]:
            raise Exception(
                "Invalid period: the starting date must be greater "
                "than the ending date."
            )
        self.dates = dates

    def size(self):
        """Return the total amount of days between two dates"""
        return (self.dates[1] - self.dates[0]).days


class CalendarRangePeriod(DateRangePeriod):
    """
    A CalendarRangePeriod is a DateRangePeriod which uses a Calendar to
    compute the amount of days contained into the underlying period.
    """

    def __init__(self, period, calendar):
        super().__init__(period.dates, unit="day")
        self.calendar = calendar

    def size(self):
        "Return the amount of working days into period."
        d1 = self.dates[0].isoformat()
        d2 = self.dates[1].isoformat()
        return self.calendar.bizdays((d1, d2))


class DayCount:
    """DayCount"""

    _daycounts = {
        "30/360": None,
        "30/360 US": None,
        "30E/360 ISDA": None,
        "30E+/360": None,
        "actual/365": 365,
        "actual/360": 360,
        "actual/364": 364,
        "actual/365L": 365,
        "business/252": 252,
    }

    def __init__(self, dc):
        if dc not in self.names:
            raise Exception("Invalid day count: %s" % dc)
        self._name = dc
        self._daycount = dc
        self._daysinbase = self._daycounts[dc]
        self._unitsize = {  # frequency multiplier
            "year": 1,
            "half-year": 2,
            "quarter": 4,
            "month": 12,
            "day": self._daysinbase,
        }
        self._unit_convert = {
            "year": {
                "day": self._daysinbase,
                "month": 12,
                "quarter": 4,
                "half-year": 2,
                "year": 1,
            },
            "half-year": {
                "day": self._daysinbase / 2.0,
                "month": 6,
                "quarter": 2,
                "half-year": 1,
                "year": 0.5,
            },
            "quarter": {
                "day": self._daysinbase / 4.0,
                "month": 3,
                "quarter": 1,
                "half-year": 0.5,
                "year": 1 / 4.0,
            },
            "month": {
                "day": self._daysinbase / 12.0,
                "month": 1,
                "quarter": 3,
                "half-year": 6,
                "year": 12,
            },
            "day": {
                "day": 1,
                "month": 12.0 / self._daysinbase,
                "quarter": 4.0 / self._daysinbase,
                "half-year": 2.0 / self._daysinbase,
                "year": 1.0 / self._daysinbase,
            },
        }

    def __getdaysinbase(self):
        """
        Private get method for the read-only property daysinbase.
        """
        return self._daysinbase

    daysinbase = property(__getdaysinbase)

    def __get_name(self):
        return self._name

    name = property(__get_name)

    def __eq__(self, other):
        return self._daycount == other._daycount

    def in_unit(self, period, unit):
        """
        Returns the size of the period converted to the given unit.
        """
        return np.asarray(period.size()) * self._unit_convert[period.unit][unit]

    def day(self, period):
        """
        Returns the size of the period converted to the given unit.
        """
        return np.asarray(period.size()) * self._unit_convert[period.unit]["day"]

    def month(self, period):
        """
        Returns the size of the period converted to the given unit.
        """
        return np.asarray(period.size()) * self._unit_convert[period.unit]["month"]

    def quarter(self, period):
        """
        Returns the size of the period converted to the given unit.
        """
        return np.asarray(period.size()) * self._unit_convert[period.unit]["quarter"]

    def half_year(self, period):
        """
        Returns the size of the period converted to the given unit.
        """
        return np.asarray(period.size()) * self._unit_convert[period.unit]["half-year"]

    def year(self, period):
        """
        Returns the size of the period converted to the given unit.
        """
        return np.asarray(period.size()) * self._unit_convert[period.unit]["year"]

    def daysinunit(self, unit):
        """
        daysinunit method returns the amount of days in base, for a given time
        unit (year, month, day, ...). For example, the business/252 day count
        rule has 252 days in base, so if you have a period of time with a time
        unit of month then you use 21 days for each month.
        """
        return float(self.daysinbase) / self.unitsize(unit)

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
        days = np.asarray(period.size()) * self.daysinunit(period.unit)
        return np.asarray(days, dtype=np.float64) / self.daysinbase

    def timefreq(self, period, frequency):
        """
        timefreq returns the amount of time contained into the period adjusted
        to the given frequency.
        """
        tf = self.timefactor(period)
        return np.asarray(tf, dtype=np.float64) * self.unitsize(frequency.unit())


DayCount.names = tuple(DayCount._daycounts.keys())


class Frequency:
    _units = {  # frequency to time unit mapping
        # adjective : noun
        "annual": "year",
        "semi-annual": "half-year",
        "quarterly": "quarter",
        "monthly": "month",
        "daily": "day",
    }

    def __init__(self, name):
        if name not in self.names:
            raise Exception("Invalid frequency: %s" % name)
        self._name = name

    def __eq__(self, other):
        return self.name == other.name

    def __get_name(self):
        return self._name

    name = property(__get_name)

    def unit(self):
        return self._units[self.name]


Frequency.names = tuple(Frequency._units.keys())


class TimeUnit:
    names = tuple(Frequency._units.values())


class Compounding:
    _funcs = {
        "simple": lambda r, t: 1 + np.asarray(r) * np.asarray(t),
        "compounded": lambda r, t: (1 + np.asarray(r)) ** np.asarray(t),
        "continuous": lambda r, t: np.exp(np.asarray(r) * np.asarray(t)),
    }

    def __init__(self, name):
        if name not in self.names:
            raise Exception("Invalid compounding: %s" % name)
        self._name = name

    def __call__(self, r, t):
        return self._funcs[self.name](r, t)

    def __eq__(self, other):
        return self.name == other.name

    def __get_name(self):
        return self._name

    name = property(__get_name)


# TODO: This code is a malign hack. I might use a metaclass here.
Compounding.names = tuple([i for i in Compounding._funcs.keys()])
for k, v in Compounding._funcs.items():
    setattr(Compounding, k, staticmethod(v))


class InterestRate:
    """
    InterestRate class

    This class receives a calendar instance in its constructor's parameter list
    because in some cases it's fairly common to user provide that information.
    Despite of having a default calendar set either into the system or for a
    given market, we are likely to handle the situation where interest rate
    has its own calendar and that calendar must be used to discount the
    cashflows.
    
    The rate parameter can be a scalar or an array-like object (numpy array, 
    pandas Series, or Polars Series) for vectorized calculations.
    """

    # TODO write conversion functions: given other settings generate a different rate
    def __init__(self, rate, frequency, compounding, daycount, calendar=None):
        self.rate = rate
        self.frequency = frequency
        self.daycount = daycount
        self.compounding = compounding
        self.daycount = daycount
        self.calendar = calendar
        if self.calendar and not self.daycount.name.startswith("business"):
            raise Exception("%s DayCount cannot accept calendar" % self.daycount.name)

    def discount(self, period):
        """Return the discount factor"""
        return 1.0 / self.compound(period)

    def compound(self, period):
        """Return the compounding factor"""
        if self.calendar:
            period = CalendarRangePeriod(period, self.calendar)

        t = self.daycount.timefreq(period, self.frequency)
        result = self.compounding(self.rate, t)
        # Return as numpy array for consistent handling
        return np.asarray(result)


# Add vectorized module-level functions for Pandas/Polars compatibility
def _to_numpy_array(arr):
    """Convert array-like objects (pandas Series, Polars Series) to numpy array."""
    if hasattr(arr, 'to_numpy'):
        # Works for both pandas and Polars
        return arr.to_numpy()
    elif hasattr(arr, '__array__'):
        return np.asarray(arr)
    return arr


def compound(ir, period):
    """
    Return the compounding factor regarding an interest rate and a period.
    
    Supports vectorized operations with numpy arrays, pandas Series, and Polars Series.
    """
    return ir.compound(period)


def discount(ir, period):
    """
    Return the discount factor regarding an interest rate and a period.
    
    Supports vectorized operations with numpy arrays, pandas Series, and Polars Series.
    """
    return ir.discount(period)
