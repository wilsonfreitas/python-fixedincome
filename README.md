**python-fixedincome** is a small module focused on interest rate calculations.
It promotes an easy to use approach to set and handle the *interest rate* and its attributes:

* compounding factors
* day count rules
* compounding frequency
* calendar

This module also helps with interest rate conversions and computations of compounding
factors over time periods, using either business days and actual days.

This module will allow users to create an interest rate by declaring it textually.
It is as simple as declare such a statement like `'0.06 annual simple actual/365'`.
Here we have an interest rate which yields 6% annually, uses a simple compounding (linear),
counts all days between 2 dates and considers 365 per year.
