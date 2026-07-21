import pytest

from src.analytics.cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_cfo_quality_score,
    calculate_capex_intensity,
    calculate_fcf_conversion_rate,
    classify_capital_allocation,
)


def test_free_cash_flow():
    result = calculate_free_cash_flow(
        operating_activity=100,
        investing_activity=-40,
    )

    assert result == 60


def test_negative_free_cash_flow_is_allowed():
    result = calculate_free_cash_flow(
        operating_activity=50,
        investing_activity=-100,
    )

    assert result == -50


def test_cfo_quality_high():
    result = calculate_cfo_quality_score(
        cfo_values=[120, 110, 130],
        pat_values=[100, 100, 100],
    )

    assert result["score"] == pytest.approx(1.2)
    assert result["label"] == "High Quality"


def test_cfo_quality_accrual_risk():
    result = calculate_cfo_quality_score(
        cfo_values=[30, 40, 20],
        pat_values=[100, 100, 100],
    )

    assert result["score"] == pytest.approx(0.3)
    assert result["label"] == "Accrual Risk"


def test_cfo_quality_pat_zero_returns_none_when_no_valid_period():
    result = calculate_cfo_quality_score(
        cfo_values=[100],
        pat_values=[0],
    )

    assert result["score"] is None
    assert result["label"] is None


def test_capex_intensity_asset_light():
    result = calculate_capex_intensity(
        investing_activity=-20,
        sales=1000,
    )

    assert result["percentage"] == pytest.approx(2.0)
    assert result["label"] == "Asset Light"


def test_fcf_conversion_zero_operating_profit():
    result = calculate_fcf_conversion_rate(
        free_cash_flow=100,
        operating_profit=0,
    )

    assert result is None


def test_capital_allocation_shareholder_returns():
    result = classify_capital_allocation(
        cfo=100,
        cfi=-50,
        cff=-20,
        cfo_pat_ratio=1.5,
    )

    assert result == "Shareholder Returns"


def test_capital_allocation_distress_signal():
    result = classify_capital_allocation(
        cfo=-100,
        cfi=50,
        cff=100,
    )

    assert result == "Distress Signal"


def test_capital_allocation_growth_funded_by_debt():
    result = classify_capital_allocation(
        cfo=-100,
        cfi=-200,
        cff=300,
    )

    assert result == "Growth Funded by Debt"