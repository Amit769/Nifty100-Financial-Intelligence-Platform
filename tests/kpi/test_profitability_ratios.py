import pytest

from src.analytics.ratios import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    check_opm_mismatch,
    calculate_roe,
    calculate_roce,
    calculate_roa,
)


def test_net_profit_margin_normal_case():
    result = calculate_net_profit_margin(
        net_profit=200,
        sales=1000,
    )

    assert result == pytest.approx(20.0)


def test_net_profit_margin_zero_sales_returns_none():
    result = calculate_net_profit_margin(
        net_profit=200,
        sales=0,
    )

    assert result is None


def test_operating_profit_margin_normal_case():
    result = calculate_operating_profit_margin(
        operating_profit=300,
        sales=1000,
    )

    assert result == pytest.approx(30.0)


def test_opm_cross_check_mismatch():
    computed_opm = 30.0
    source_opm = 28.5

    result = check_opm_mismatch(
        computed_opm=computed_opm,
        source_opm=source_opm,
    )

    assert result is True


def test_roe_normal_case():
    result = calculate_roe(
        net_profit=200,
        equity_capital=100,
        reserves=900,
    )

    assert result == pytest.approx(20.0)


def test_roe_negative_equity_returns_none():
    result = calculate_roe(
        net_profit=200,
        equity_capital=-100,
        reserves=50,
    )

    assert result is None


def test_roce_normal_case():
    result = calculate_roce(
        ebit=300,
        equity_capital=100,
        reserves=900,
        borrowings=500,
    )

    assert result == pytest.approx(20.0)


def test_roa_zero_assets_returns_none():
    result = calculate_roa(
        net_profit=200,
        total_assets=0,
    )

    assert result is None