"""
Screener Result Formatter
=========================

Converts raw screener results into analyst-friendly output.
"""


def format_screener_results(data):
    """
    Return a clean, analyst-friendly screener result table.
    """

    columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "sub_sector",
        "year",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "operating_profit_margin_pct",
        "interest_coverage",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "composite_quality_score",
    ]

    available_columns = [
        column
        for column in columns
        if column in data.columns
    ]

    return (
        data[available_columns]
        .copy()
        .sort_values(
            "composite_quality_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )
    
def generate_screener_summary(data):
    """
    Generate high-level summary statistics
    for screener results.
    """

    if data.empty:
        return {
            "companies_found": 0,
            "average_quality_score": None,
            "top_sector": None,
        }

    top_sector = (
        data["broad_sector"]
        .value_counts()
        .idxmax()
        if "broad_sector" in data.columns
        else None
    )

    average_score = (
        data["composite_quality_score"]
        .mean()
        if "composite_quality_score" in data.columns
        else None
    )

    return {
        "companies_found": len(data),
        "average_quality_score": average_score,
        "top_sector": top_sector,
    }