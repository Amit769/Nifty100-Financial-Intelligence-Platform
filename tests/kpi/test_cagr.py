import pytest

from src.analytics.cagr import (
    calculate_cagr,
    calculate_window_cagr,
)


def test_normal_cagr():
    result = calculate_cagr(
        start_value=100,
        end_value=121,
        years=2,
    )

    assert result["value"] == pytest.approx(10.0)
    assert result["flag"] is None


def test_positive_to_negative_decline_to_loss():
    result = calculate_cagr(
        start_value=100,
        end_value=-20,
        years=3,
    )

    assert result["value"] is None
    assert result["flag"] == "DECLINE_TO_LOSS"


def test_negative_to_positive_turnaround():
    result = calculate_cagr(
        start_value=-100,
        end_value=50,
        years=3,
    )

    assert result["value"] is None
    assert result["flag"] == "TURNAROUND"


def test_both_negative():
    result = calculate_cagr(
        start_value=-100,
        end_value=-50,
        years=3,
    )

    assert result["value"] is None
    assert result["flag"] == "BOTH_NEGATIVE"


def test_zero_base():
    result = calculate_cagr(
        start_value=0,
        end_value=100,
        years=3,
    )

    assert result["value"] is None
    assert result["flag"] == "ZERO_BASE"


def test_missing_values_are_insufficient():
    result = calculate_cagr(
        start_value=None,
        end_value=100,
        years=3,
    )

    assert result["value"] is None
    assert result["flag"] == "INSUFFICIENT"


def test_invalid_year_window_is_insufficient():
    result = calculate_cagr(
        start_value=100,
        end_value=150,
        years=0,
    )

    assert result["value"] is None
    assert result["flag"] == "INSUFFICIENT"


def test_window_cagr_normal_case():
    values = {
        2020: 100,
        2021: 110,
        2022: 121,
        2023: 133.1,
    }

    result = calculate_window_cagr(
        values=values,
        years=3,
    )

    assert result["value"] == pytest.approx(10.0)
    assert result["flag"] is None


def test_window_cagr_turnaround():
    values = {
        2020: -100,
        2021: -80,
        2022: -20,
        2023: 50,
    }

    result = calculate_window_cagr(
        values=values,
        years=3,
    )

    assert result["value"] is None
    assert result["flag"] == "TURNAROUND"


def test_window_cagr_insufficient_data():
    values = {
        2022: 100,
        2023: 110,
    }

    result = calculate_window_cagr(
        values=values,
        years=5,
    )

    assert result["value"] is None
    assert result["flag"] == "INSUFFICIENT"