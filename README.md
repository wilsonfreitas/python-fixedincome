
python-fixedincome is a small module focused on interest rate calculations.
With that it is possible to represent interest rate considering its several features such as:

* compounding factors
* day count rules
* compounding frequency
* calendar

This module also helps with interest rate conversions and computations of compounding factors over time periods, using either business days or not.

This module will allow users to create an interest rate only by declaring it with a text. It is as simple as this statement `'0.06 annual simple actual/365'`. Here we have an interest rate which yields 6% annually, uses a simple compounding, doesn't count non-working days and considers 365 per year.
