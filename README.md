# python-fixedincome

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

The module is **fully vectorized using NumPy** and provides seamless integration with
**Pandas and Polars DataFrames**. Results from calculations can be directly assigned to
DataFrame columns, enabling efficient batch processing of multiple rates and periods.

## Installation

Using uv (recommended):

```bash
uv pip install -e .
```

Or with pip:

```bash
pip install -e .
```

## Quick Start

```python
from fixedincome import ir, period, compound, discount

# Create an interest rate from a string specification
rate = ir('0.06 annual simple actual/365')

# Create a time period
p = period('1 month')

# Calculate compounding factor
factor = compound(rate, p)

# Calculate discount factor
disc = discount(rate, p)
```

### Vectorized Operations with NumPy, Pandas, and Polars

The module supports vectorized operations for efficient batch calculations:

```python
import numpy as np
import pandas as pd
from fixedincome import rates, periods, compound, discount

# Create multiple interest rates at once
rates_array = np.array([0.05, 0.06, 0.07])
ir_vector = rates(rates_array, 'annual', 'simple', 'actual/365')

# Create multiple periods at once
periods_array = np.array([1, 2, 3])
p_vector = periods(periods_array, 'month')

# Calculate compounding factors for all combinations
factors = compound(ir_vector, p_vector)

# Works seamlessly with Pandas DataFrames
df = pd.DataFrame({
    'rate': [0.05, 0.06, 0.07],
    'months': [1, 2, 3]
})
ir_df = rates(df['rate'], 'annual', 'simple', 'actual/365')
p_df = periods(df['months'], 'month')
df['compounding_factor'] = compound(ir_df, p_df)
```

### Interest Rate Specification

Interest rates can be created using a textual specification:

```python
# Simple interest, annual frequency, actual/365 day count
rate1 = ir('0.06 annual simple actual/365')

# Compounded interest, semi-annual frequency, business/252 with calendar
rate2 = ir('0.09 annual compounded business/252 calANBIMA')

# Continuous compounding, annual frequency, 30/360 day count
rate3 = ir('0.06 annual continuous 30/360')
```

### Period Specification

Periods can be specified as fixed time periods or date ranges:

```python
# Fixed time periods
p1 = period('15 days')
p2 = period('1 month')
p3 = period('1.5 years')
p4 = period('1.5 quarters')

# Date range periods
p5 = period('2012-07-12:2012-07-16')
```

## Development

This project uses modern Python tooling:

- **uv** for dependency management
- **ruff** for linting and formatting
- **pre-commit** for git hooks
- **pytest** for testing

### Setup Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository and navigate to it
git clone <repository-url>
cd python-fixedincome

# Install dependencies including dev dependencies
uv sync --dev

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Or using uv
uv run pytest
```

### Code Quality

```bash
# Run ruff linter
ruff check .

# Format code with ruff
ruff format .

# Run pre-commit on all files
pre-commit run --all-files
```

## Project Structure

```
python-fixedincome/
├── src/
│   └── fixedincome/
│       ├── __init__.py      # Module exports and version info
│       ├── core.py          # Core classes (InterestRate, DayCount, etc.) with NumPy vectorization
│       └── utils.py         # Utility functions (ir, period, compound, discount, rates, periods)
├── tests/
│   └── test_fixedincome.py
├── pyproject.toml
├── README.md
├── .pre-commit-config.yaml
└── ...
```

## Dependencies

- **numpy**: For vectorized numerical operations
- **bizdays**: For business day calendar calculations

## License

MIT License
