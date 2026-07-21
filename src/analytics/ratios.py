"""
Profitability ratio calculations for the NIFTY 100 Financial Intelligence Platform.

All functions are intentionally pure calculations so they can be:
- tested independently,
- reused by the ETL/ratio engine,
- applied to database records later.
"""


def calculate_net_profit_margin(net_profit, sales):
    """
    Calculate Net Profit Margin.

    Formula:
        (Net Profit / Sales) * 100

    Returns:
        float | None
    """
    if sales is None or sales == 0:
        return None

    if net_profit is None:
        return None

    return (net_profit / sales) * 100


def calculate_operating_profit_margin(operating_profit, sales):
    """
    Calculate Operating Profit Margin.

    Formula:
        (Operating Profit / Sales) * 100

    Returns:
        float | None
    """
    if sales is None or sales == 0:
        return None

    if operating_profit is None:
        return None

    return (operating_profit / sales) * 100


def check_opm_mismatch(computed_opm, source_opm, threshold=1.0):
    """
    Compare computed OPM with the source OPM value.

    A mismatch is flagged when the absolute difference exceeds
    the configured threshold.

    Returns:
        bool
    """
    if computed_opm is None or source_opm is None:
        return False

    return abs(computed_opm - source_opm) > threshold


def calculate_roe(net_profit, equity_capital, reserves):
    """
    Calculate Return on Equity.

    Formula:
        (Net Profit / (Equity Capital + Reserves)) * 100

    Returns None when total equity is zero or negative.
    """
    if net_profit is None:
        return None

    if equity_capital is None:
        equity_capital = 0

    if reserves is None:
        reserves = 0

    total_equity = equity_capital + reserves

    if total_equity <= 0:
        return None

    return (net_profit / total_equity) * 100


def calculate_roce(
    ebit,
    equity_capital,
    reserves,
    borrowings,
):
    """
    Calculate Return on Capital Employed.

    Formula:
        (EBIT / (Equity + Reserves + Borrowings)) * 100

    Returns None when capital employed is zero or negative.
    """
    if ebit is None:
        return None

    equity_capital = equity_capital or 0
    reserves = reserves or 0
    borrowings = borrowings or 0

    capital_employed = (
        equity_capital
        + reserves
        + borrowings
    )

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def calculate_roa(net_profit, total_assets):
    """
    Calculate Return on Assets.

    Formula:
        (Net Profit / Total Assets) * 100

    Returns None when total assets are zero.
    """
    if net_profit is None:
        return None

    if total_assets is None or total_assets == 0:
        return None

    return (net_profit / total_assets) * 100

def calculate_debt_to_equity(
    borrowings,
    equity_capital,
    reserves,
):
    """
    Calculate Debt-to-Equity ratio.

    Formula:
        Borrowings / (Equity Capital + Reserves)

    Special cases:
        - Borrowings = 0 -> 0
        - Equity <= 0 -> None

    Returns:
        float | None
    """
    if borrowings is None:
        borrowings = 0

    if borrowings == 0:
        return 0

    equity_capital = equity_capital or 0
    reserves = reserves or 0

    total_equity = equity_capital + reserves

    if total_equity <= 0:
        return None

    return borrowings / total_equity


def calculate_high_leverage_flag(
    debt_to_equity,
    broad_sector,
    threshold=5.0,
):
    """
    Flag companies with unusually high leverage.

    Financials companies are excluded because high leverage
    is structurally normal in banks, NBFCs, and insurers.
    """
    if debt_to_equity is None:
        return False

    if broad_sector == "Financials":
        return False

    return debt_to_equity > threshold


def calculate_interest_coverage(
    operating_profit,
    other_income,
    interest,
):
    """
    Calculate Interest Coverage Ratio.

    Formula:
        (Operating Profit + Other Income) / Interest

    Returns:
        float | None

    Interest = 0 is treated as debt-free and returns None.
    """
    if interest is None or interest == 0:
        return None

    operating_profit = operating_profit or 0
    other_income = other_income or 0

    return (operating_profit + other_income) / interest


def get_icr_label(interest_coverage):
    """
    Return a display label for interest coverage.

    None means the company has no interest expense and is
    therefore treated as debt-free for this KPI.
    """
    if interest_coverage is None:
        return "Debt Free"

    return None


def calculate_icr_warning(
    interest_coverage,
    threshold=1.5,
):
    """
    Flag companies whose interest coverage is below the
    defined safety threshold.
    """
    if interest_coverage is None:
        return False

    return interest_coverage < threshold


def calculate_net_debt(
    borrowings,
    investments,
):
    """
    Calculate Net Debt.

    Formula:
        Borrowings - Investments
    """
    borrowings = borrowings or 0
    investments = investments or 0

    return borrowings - investments


def calculate_asset_turnover(
    sales,
    total_assets,
):
    """
    Calculate Asset Turnover.

    Formula:
        Sales / Total Assets
    """
    if total_assets is None or total_assets == 0:
        return None

    if sales is None:
        return None

    return sales / total_assets