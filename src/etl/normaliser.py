"""
normaliser.py

Utility functions for standardizing company identifiers
and financial year labels across all datasets.
"""

from __future__ import annotations

import re
import pandas as pd


def normalize_ticker(value: str | None) -> str | None:
    """
    Standardize company ticker/company_id.

    Examples
    --------
    ' tcs '      -> 'TCS'
    'infy'       -> 'INFY'
    ' HDFCBANK ' -> 'HDFCBANK'
    None         -> None
    """

    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    if value == "":
        return None

    return value


def normalize_year(value: str | int | float | None) -> str | None:
    """
    Convert different year formats into YYYY-MM.

    Supported
    ---------
    Mar-23      -> 2023-03
    Mar 23      -> 2023-03
    Mar-2023    -> 2023-03
    Dec-23      -> 2023-12
    2023        -> 2023
    FY23        -> 2023
    FY2023      -> 2023

    Invalid values return None.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    month_map = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
    }

    text = value.upper().replace("/", "-").replace(" ", "-")

    # Mar-23 / Mar-2023
    match = re.fullmatch(r"([A-Z]{3})-(\d{2,4})", text)

    if match:
        month, year = match.groups()

        if len(year) == 2:
            year = f"20{year}"

        if month in month_map:
            return f"{year}-{month_map[month]}"

    # FY23 / FY2023
    match = re.fullmatch(r"FY(\d{2,4})", text)

    if match:
        year = match.group(1)

        if len(year) == 2:
            year = f"20{year}"

        return year

    # Plain year
    if re.fullmatch(r"\d{4}", text):
        return text

    return None