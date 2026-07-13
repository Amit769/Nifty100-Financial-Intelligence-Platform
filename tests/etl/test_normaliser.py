"""
Unit tests for normaliser.py
"""

import pytest

from src.etl.normaliser import normalize_ticker, normalize_year


# ==========================================================
# normalize_ticker()
# ==========================================================

@pytest.mark.parametrize(
    "value, expected",
    [
        ("tcs", "TCS"),
        (" TCS ", "TCS"),
        ("infy", "INFY"),
        ("HDFCBANK", "HDFCBANK"),
        ("hdfcbank", "HDFCBANK"),
        (" Reliance ", "RELIANCE"),
        ("", None),
        (None, None),
    ],
)
def test_normalize_ticker(value, expected):
    assert normalize_ticker(value) == expected


# ==========================================================
# normalize_year()
# ==========================================================

@pytest.mark.parametrize(
    "value, expected",
    [
        ("Mar-23", "2023-03"),
        ("Mar 23", "2023-03"),
        ("Mar-2023", "2023-03"),
        ("DEC-24", "2024-12"),
        ("Jan-22", "2022-01"),
        ("FY23", "2023"),
        ("FY24", "2024"),
        ("FY2023", "2023"),
        ("2022", "2022"),
        ("2024", "2024"),
        ("", None),
        (None, None),
        ("abcd", None),
        ("XYZ", None),
        ("FY", None),
        ("13-2023", None),
        ("Mar", None),
        ("202", None),
        ("20235", None),
    ],
)
def test_normalize_year(value, expected):
    assert normalize_year(value) == expected
    
    # ==========================================================
# Extra edge cases
# ==========================================================

@pytest.mark.parametrize(
    "value",
    [
        "   ",
        "*****",
        "@@@",
        "FYXX",
        "Month23",
        "99999",
        "0",
        "-",
        "////",
    ],
)
def test_invalid_year_returns_none(value):
    assert normalize_year(value) is None


@pytest.mark.parametrize(
    "value",
    [
        "abc",
        " abc ",
        "company1",
        "xyz123",
        "l&t",
        "asianpaints",
        "itc",
        "sbin",
        "nestleindia",
    ],
)
def test_ticker_uppercase(value):
    result = normalize_ticker(value)

    if result is not None:
        assert result == result.upper()