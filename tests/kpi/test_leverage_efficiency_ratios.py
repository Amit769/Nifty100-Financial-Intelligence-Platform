import pytest

from src.analytics.ratios import (
    calculate_debt_to_equity,
    calculate_high_leverage_flag,
    calculate_interest_coverage,
    get_icr_label,
    calculate_icr_warning,
    calculate_net_debt,
    calculate_asset_turnover,
)


def test_debt_to_equity_normal_case():
    result = calculate_debt_to_equity(
        borrowings=500,
        equity_capital=100,
        reserves=900,
    )

    assert result == pytest.approx(0.5)


def test_debt_to_equity_debt_free_returns_zero():
    result = calculate_debt_to_equity(
        borrowings=0,
        equity_capital=100,
        reserves=900,
    )

    assert result == 0


def test_high_leverage_flag_non_financial_company():
    result = calculate_high_leverage_flag(
        debt_to_equity=6.0,
        broad_sector="Technology",
    )

    assert result is True


def test_high_leverage_flag_suppressed_for_financials():
    result = calculate_high_leverage_flag(
        debt_to_equity=6.0,
        broad_sector="Financials",
    )

    assert result is False


def test_interest_coverage_normal_case():
    result = calculate_interest_coverage(
        operating_profit=300,
        other_income=100,
        interest=100,
    )

    assert result == pytest.approx(4.0)


def test_interest_zero_returns_none():
    result = calculate_interest_coverage(
        operating_profit=300,
        other_income=100,
        interest=0,
    )

    assert result is None


def test_icr_none_gets_debt_free_label():
    result = get_icr_label(None)

    assert result == "Debt Free"


def test_icr_warning_below_threshold():
    result = calculate_icr_warning(1.2)

    assert result is True