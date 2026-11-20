from datetime import date
from decimal import Decimal

import pytest

from app.services.depreciation import (
    DepreciationParams,
    STRAIGHT_LINE,
    REDUCING_BALANCE,
    accumulated_at,
    annual_schedule,
    compute_position,
    gain_or_loss_on_disposal,
    months_between,
    validate_params,
)

D = Decimal


def sl(cost="1200000", residual="200000", life="5", start=date(2024, 1, 1)):
    return DepreciationParams(D(cost), D(residual), D(life), STRAIGHT_LINE, start)


def rb(cost="1000", residual="100", life="2", rate=None, start=date(2024, 1, 1)):
    return DepreciationParams(D(cost), D(residual), D(life), REDUCING_BALANCE, start, D(rate) if rate else None)


def test_months_between_whole_months():
    assert months_between(date(2024, 1, 15), date(2024, 3, 14)) == 1
    assert months_between(date(2024, 1, 15), date(2024, 3, 15)) == 2
    assert months_between(date(2024, 1, 1), date(2023, 12, 1)) == 0


def test_straight_line_annual_charge():
    pos = compute_position(sl(), date(2025, 1, 1))
    assert pos.months_elapsed == 12
    assert pos.accumulated == D("200000.00")  # (1,200,000 - 200,000) / 5
    assert pos.carrying_amount == D("1000000.00")
    assert pos.annual_depreciation == D("200000.00")
    assert not pos.fully_depreciated


def test_straight_line_part_year_is_pro_rata():
    pos = compute_position(sl(), date(2024, 7, 1))
    assert pos.accumulated == D("100000.00")  # 6 months


def test_depreciation_never_below_residual_and_stops():
    pos = compute_position(sl(), date(2040, 1, 1))
    assert pos.accumulated == D("1000000.00")
    assert pos.carrying_amount == D("200000.00")
    assert pos.fully_depreciated
    assert pos.annual_depreciation == D("0.00")
    assert pos.remaining_months == 0


def test_not_started_yet_has_no_depreciation():
    pos = compute_position(sl(start=date(2030, 1, 1)), date(2026, 1, 1))
    assert pos.accumulated == D("0.00")
    assert pos.carrying_amount == D("1200000.00")


def test_reducing_balance_explicit_rate():
    p = rb(cost="1000", residual="0", life="5", rate="0.4")
    assert compute_position(p, date(2025, 1, 1)).carrying_amount == D("600.00")
    assert compute_position(p, date(2026, 1, 1)).carrying_amount == D("360.00")


def test_reducing_balance_derived_rate_reaches_residual_at_end_of_life():
    p = rb(cost="1000", residual="100", life="2")
    end = compute_position(p, date(2026, 1, 1))
    assert end.carrying_amount == D("100.00")
    assert end.fully_depreciated


def test_reducing_balance_default_double_declining_when_no_residual():
    p = rb(cost="1000", residual="0", life="5")  # rate = 2/5 = 40%
    assert compute_position(p, date(2025, 1, 1)).carrying_amount == D("600.00")


def test_disposal_freezes_depreciation():
    pos = compute_position(sl(), date(2030, 1, 1), disposal_date=date(2025, 1, 1))
    assert pos.accumulated == D("200000.00")
    assert pos.annual_depreciation == D("0.00")


def test_schedule_reconciles():
    rows = annual_schedule(sl())
    assert len(rows) == 5
    assert sum(r["depreciation_expense"] for r in rows) == D("1000000.00")
    assert rows[-1]["closing_carrying_amount"] == D("200000.00")
    for r in rows:
        assert r["opening_carrying_amount"] - r["depreciation_expense"] == r["closing_carrying_amount"]


def test_schedule_reducing_balance_reconciles():
    rows = annual_schedule(rb(cost="1000", residual="100", life="3"))
    assert sum(r["depreciation_expense"] for r in rows) == D("900.00")
    assert rows[-1]["closing_carrying_amount"] == D("100.00")


def test_accumulated_at_matches_position():
    p = sl()
    assert accumulated_at(p, 30) == compute_position(p, date(2026, 7, 1)).accumulated


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(cost="0"),
        dict(cost="-5"),
        dict(residual="1300000"),
        dict(residual="-1"),
        dict(life="0"),
    ],
)
def test_validation_rules(kwargs):
    with pytest.raises(ValueError):
        validate_params(sl(**kwargs))


def test_unknown_method_rejected():
    bad = DepreciationParams(D(100), D(0), D(5), "magic", date(2024, 1, 1))
    with pytest.raises(ValueError):
        validate_params(bad)


def test_gain_and_loss_on_disposal():
    assert gain_or_loss_on_disposal(D("150000"), D("100000")) == D("50000.00")
    assert gain_or_loss_on_disposal(D("40000"), D("100000")) == D("-60000.00")
    assert gain_or_loss_on_disposal(D("0"), D("0")) == D("0.00")
