"""
CAGR calculations for the NIFTY 100 Financial Intelligence Platform.

The engine explicitly handles financial time-series edge cases:
- positive to positive
- positive to negative
- negative to positive
- negative to negative
- zero base
- insufficient history
"""


def calculate_cagr(start_value, end_value, years):
    """
    Calculate Compound Annual Growth Rate.

    Formula:
        ((end / start) ** (1 / years) - 1) * 100

    Returns:
        dict:
            {
                "value": float | None,
                "flag": str | None
            }
    """

    if years is None or years <= 0:
        return {
            "value": None,
            "flag": "INSUFFICIENT",
        }

    if start_value is None or end_value is None:
        return {
            "value": None,
            "flag": "INSUFFICIENT",
        }

    if start_value == 0:
        return {
            "value": None,
            "flag": "ZERO_BASE",
        }

    if start_value > 0 and end_value > 0:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

        return {
            "value": cagr,
            "flag": None,
        }

    if start_value > 0 and end_value < 0:
        return {
            "value": None,
            "flag": "DECLINE_TO_LOSS",
        }

    if start_value < 0 and end_value > 0:
        return {
            "value": None,
            "flag": "TURNAROUND",
        }

    if start_value < 0 and end_value < 0:
        return {
            "value": None,
            "flag": "BOTH_NEGATIVE",
        }

    return {
        "value": None,
        "flag": "INSUFFICIENT",
    }


def calculate_window_cagr(values, years):
    """
    Calculate CAGR using a time-series mapping.

    Example:
        values = {
            2020: 100,
            2021: 110,
            2022: 125,
            2023: 150,
            2024: 180,
        }

    For a 3-year CAGR:
        start = 2021
        end = 2024

    Returns:
        dict with value and flag.
    """

    if values is None:
        return {
            "value": None,
            "flag": "INSUFFICIENT",
        }

    if years is None or years <= 0:
        return {
            "value": None,
            "flag": "INSUFFICIENT",
        }

    clean_values = {
        int(year): value
        for year, value in values.items()
        if value is not None
    }

    available_years = sorted(clean_values.keys())

    if len(available_years) < years + 1:
        return {
            "value": None,
            "flag": "INSUFFICIENT",
        }

    end_year = available_years[-1]
    start_year = end_year - years

    if start_year not in clean_values:
        return {
            "value": None,
            "flag": "INSUFFICIENT",
        }

    return calculate_cagr(
        start_value=clean_values[start_year],
        end_value=clean_values[end_year],
        years=years,
    )