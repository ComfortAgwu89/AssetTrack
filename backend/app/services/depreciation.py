"""Depreciation engine (pure Python, no database access).

Conventions (documented so every figure can be reproduced and audited):

* Depreciation runs in whole completed months from the depreciation start date.
  A part-year is therefore charged pro rata (6 months = half a year).
* Depreciable amount = acquisition cost - residual value. Accumulated
  depreciation never exceeds it, so carrying amount never drops below residual.
* Straight line: charge = depreciable amount x months / (useful life x 12).
* Reducing balance: carrying amount = cost x (1 - rate) ** (months / 12), floored
  at residual value. If no rate is supplied it is derived as
  1 - (residual / cost) ** (1 / life) when residual > 0, otherwise the
  double-declining rate 2 / life (capped at 100%).
* Depreciation stops at the end of the useful life. With a custom reducing
  balance rate the carrying amount at that point may remain above residual;
  the asset is still reported as fully depreciated because its life has ended.
* For a disposed asset, pass the disposal date: depreciation is frozen there.

These are management figures, not audited financial statements.
"""
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
import calendar
import math

STRAIGHT_LINE = "straight_line"
REDUCING_BALANCE = "reducing_balance"
METHODS = (STRAIGHT_LINE, REDUCING_BALANCE)

CENT = Decimal("0.01")


def _d(value):
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _q(value):
    return _d(value).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class DepreciationParams:
    cost: Decimal
    residual: Decimal
    useful_life_years: Decimal
    method: str
    start_date: date
    rate: Decimal = None  # annual rate as a fraction, e.g. Decimal("0.25")


@dataclass(frozen=True)
class Position:
    months_elapsed: int
    total_months: int
    accumulated: Decimal
    carrying_amount: Decimal
    annual_depreciation: Decimal
    remaining_months: int
    fully_depreciated: bool


def validate_params(p):
    """Raise ValueError if the accounting rules are violated."""
    cost, residual, life = _d(p.cost), _d(p.residual), _d(p.useful_life_years)
    if cost <= 0:
        raise ValueError("Acquisition cost must be greater than zero.")
    if residual < 0:
        raise ValueError("Residual value cannot be negative.")
    if residual > cost:
        raise ValueError("Residual value cannot exceed acquisition cost.")
    if life <= 0:
        raise ValueError("Useful life must be greater than zero.")
    if p.method not in METHODS:
        raise ValueError(f"Unknown depreciation method: {p.method}")
    if p.rate is not None and not (Decimal(0) < _d(p.rate) <= Decimal(1)):
        raise ValueError("Depreciation rate must be between 0 and 100%.")


def total_months(p):
    return int((_d(p.useful_life_years) * 12).to_integral_value(rounding=ROUND_HALF_UP))


def months_between(start, end):
    """Whole completed months from start to end (0 if end is before start)."""
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return max(months, 0)


def add_months(d, months):
    index = d.month - 1 + months
    year, month = d.year + index // 12, index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def resolve_rate(p):
    """Annual reducing-balance rate as a float fraction."""
    if p.rate is not None:
        return float(p.rate)
    cost, residual, life = float(p.cost), float(p.residual), float(p.useful_life_years)
    if residual > 0:
        return 1 - (residual / cost) ** (1 / life)
    return min(2 / life, 1.0)


def accumulated_at(p, months):
    """Accumulated depreciation after `months` completed months."""
    validate_params(p)
    cost, residual = _d(p.cost), _d(p.residual)
    depreciable = cost - residual
    months = max(0, min(months, total_months(p)))
    if depreciable == 0 or months == 0:
        return Decimal("0.00")
    if p.method == STRAIGHT_LINE:
        accumulated = depreciable * months / total_months(p)
    else:
        rate = resolve_rate(p)
        carrying = float(cost) * (1 - rate) ** (months / 12)
        accumulated = Decimal(str(float(cost) - carrying))
    accumulated = min(max(accumulated, Decimal(0)), depreciable)
    return _q(accumulated)


def compute_position(p, as_of, disposal_date=None):
    """Depreciation position at `as_of` (frozen at disposal_date if given)."""
    effective = min(as_of, disposal_date) if disposal_date else as_of
    months = min(months_between(p.start_date, effective), total_months(p))
    accumulated = accumulated_at(p, months)
    cost, residual = _q(p.cost), _q(p.residual)
    carrying = cost - accumulated
    life_ended = months >= total_months(p)
    fully = life_ended or carrying <= residual
    if fully or disposal_date and disposal_date <= as_of:
        annual = Decimal("0.00")
    else:
        annual = accumulated_at(p, months + 12) - accumulated
    return Position(
        months_elapsed=months,
        total_months=total_months(p),
        accumulated=accumulated,
        carrying_amount=carrying,
        annual_depreciation=annual,
        remaining_months=max(total_months(p) - months, 0),
        fully_depreciated=fully,
    )


def annual_schedule(p):
    """Year-by-year schedule across the whole useful life (anniversary years)."""
    validate_params(p)
    cost = _q(p.cost)
    rows = []
    years = math.ceil(total_months(p) / 12)
    for n in range(1, years + 1):
        opening_acc = accumulated_at(p, 12 * (n - 1))
        closing_acc = accumulated_at(p, 12 * n)
        rows.append(
            {
                "year": n,
                "period_start": add_months(p.start_date, 12 * (n - 1)),
                "period_end": add_months(p.start_date, min(12 * n, total_months(p))),
                "opening_carrying_amount": cost - opening_acc,
                "depreciation_expense": closing_acc - opening_acc,
                "accumulated_depreciation": closing_acc,
                "closing_carrying_amount": cost - closing_acc,
            }
        )
    return rows


def gain_or_loss_on_disposal(proceeds, carrying_amount_at_disposal):
    """Gain (positive) or loss (negative) = proceeds - carrying amount."""
    return _q(_d(proceeds) - _d(carrying_amount_at_disposal))
