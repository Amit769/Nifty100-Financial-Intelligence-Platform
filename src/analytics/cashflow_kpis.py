"""
Cash flow KPI calculations for the NIFTY 100 Financial Intelligence Platform.
"""


def calculate_free_cash_flow(
    operating_activity,
    investing_activity,
):
    """
    Calculate Free Cash Flow.

    Formula:
        Operating Activity + Investing Activity

    Negative FCF is valid and must not be converted to None.
    """
    if operating_activity is None and investing_activity is None:
        return None

    operating_activity = operating_activity or 0
    investing_activity = investing_activity or 0

    return operating_activity + investing_activity


def calculate_cfo_quality_score(
    cfo_values,
    pat_values,
):
    """
    Calculate the average CFO/PAT ratio over available periods.

    Quality classification:
        > 1.0       -> High Quality
        0.5 to 1.0  -> Moderate
        < 0.5       -> Accrual Risk

    Returns:
        dict:
            {
                "score": float | None,
                "label": str | None
            }

    Individual periods with PAT = 0 are excluded because the
    ratio is mathematically undefined.
    """
    ratios = []

    for cfo, pat in zip(cfo_values, pat_values):
        if cfo is None or pat is None or pat == 0:
            continue

        ratios.append(cfo / pat)

    if not ratios:
        return {
            "score": None,
            "label": None,
        }

    score = sum(ratios) / len(ratios)

    if score > 1.0:
        label = "High Quality"
    elif score >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return {
        "score": score,
        "label": label,
    }


def calculate_capex_intensity(
    investing_activity,
    sales,
):
    """
    Calculate CapEx Intensity.

    Formula:
        abs(Investing Activity) / Sales * 100

    Classification:
        < 3%       -> Asset Light
        3% to 8%   -> Moderate
        > 8%       -> Capital Intensive
    """
    if investing_activity is None or sales is None or sales == 0:
        return {
            "percentage": None,
            "label": None,
        }

    percentage = abs(investing_activity) / sales * 100

    if percentage < 3:
        label = "Asset Light"
    elif percentage <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return {
        "percentage": percentage,
        "label": label,
    }


def calculate_fcf_conversion_rate(
    free_cash_flow,
    operating_profit,
):
    """
    Calculate FCF Conversion Rate.

    Formula:
        FCF / Operating Profit * 100
    """
    if (
        free_cash_flow is None
        or operating_profit is None
        or operating_profit == 0
    ):
        return None

    return free_cash_flow / operating_profit * 100


def _sign(value):
    """
    Convert a cash flow value into its sign representation.
    """
    if value is None or value == 0:
        return "0"

    if value > 0:
        return "+"

    return "-"


def classify_capital_allocation(
    cfo,
    cfi,
    cff,
    cfo_pat_ratio=None,
):
    """
    Classify capital allocation based on CFO, CFI, and CFF signs.

    Patterns:

        (+,-,-) -> Reinvestor
        (+,-,-) with high CFO/PAT -> Shareholder Returns
        (+,+,-) -> Liquidating Assets
        (-,+,+) -> Distress Signal
        (-,-,+) -> Growth Funded by Debt
        (+,+,+) -> Cash Accumulator
        (-,-,-) -> Pre-Revenue
        (+,-,+) -> Mixed

    High CFO/PAT is treated as an override for the
    (+,-,-) pattern.
    """
    pattern = (
        _sign(cfo),
        _sign(cfi),
        _sign(cff),
    )

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"

        return "Reinvestor"

    if pattern == ("+", "+", "-"):
        return "Liquidating Assets"

    if pattern == ("-", "+", "+"):
        return "Distress Signal"

    if pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if pattern == ("+", "+", "+"):
        return "Cash Accumulator"

    if pattern == ("-", "-", "-"):
        return "Pre-Revenue"

    if pattern == ("+", "-", "+"):
        return "Mixed"

    return "Unclassified"