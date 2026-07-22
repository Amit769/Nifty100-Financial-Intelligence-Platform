"""
Screener Engine
===============

Loads analyst-defined threshold filters and applies them to the
latest available financial data for the Nifty 100 universe.
"""

from pathlib import Path

import sqlite3
import yaml
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "nifty100.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "screener_config.yaml"


FILTER_COLUMN_MAP = {
    "roe_min": "return_on_equity_pct",
    "debt_to_equity_max": "debt_to_equity",
    "free_cash_flow_min": "free_cash_flow_cr",
    "revenue_cagr_5yr_min": "revenue_cagr_5yr",
    "pat_cagr_5yr_min": "pat_cagr_5yr",
    "opm_min": "operating_profit_margin_pct",
    "pe_max": "pe_ratio",
    "pb_max": "pb_ratio",
    "dividend_yield_min": "dividend_yield_pct",
    "icr_min": "interest_coverage",
    "market_cap_min": "market_cap_crore",
    "net_profit_min": "net_profit",
    "eps_cagr_min": "eps_cagr_5yr",
    "asset_turnover_min": "asset_turnover",
    "sales_min": "sales",
    "dividend_payout_max": "dividend_payout_ratio_pct",
    "revenue_cagr_3yr_min": "revenue_cagr_3yr",
}


def load_screener_config(config_path=CONFIG_PATH):
    """
    Load threshold configuration from YAML.
    """

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    return config.get("filters", {})


def period_priority(period):
    """
    Assign priority to financial periods.

    TTM is preferred over the latest annual period.
    """

    period = str(period).strip()

    if period == "TTM":
        return 10000

    if period == "Mar 2024":
        return 2024

    if period.startswith("Mar "):
        try:
            return int(period.split()[-1])
        except ValueError:
            return 0

    if period.startswith("Sep "):
        try:
            return int(period.split()[-1]) - 0.5
        except ValueError:
            return 0

    if period.startswith("Jun "):
        try:
            return int(period.split()[-1]) - 0.25
        except ValueError:
            return 0

    if period.startswith("Dec "):
        try:
            return int(period.split()[-1])
        except ValueError:
            return 0

    return 0


def load_latest_financial_data(database_path=DATABASE_PATH):
    """
    Load one latest financial record per company.

    The screener combines:
    - financial ratios
    - company metadata
    - sector classification
    - market valuation data
    - profit and loss data
    """

    connection = sqlite3.connect(database_path)

    try:
        ratios = pd.read_sql_query(
            """
            SELECT *
            FROM financial_ratios
            """,
            connection,
        )

        companies = pd.read_sql_query(
            """
            SELECT
                id AS company_id,
                company_name
            FROM companies
            """,
            connection,
        )

        sectors = pd.read_sql_query(
    """
    SELECT
        company_id,
        broad_sector,
        sub_sector
    FROM sectors
    """,
    connection,
)

        market_cap = pd.read_sql_query(
            """
            SELECT *
            FROM market_cap
            """,
            connection,
        )

        profit_loss = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                sales,
                net_profit
            FROM profitandloss
            """,
            connection,
        )

    finally:
        connection.close()

    # Select latest ratio record per company
    ratios["year_text"] = ratios["year"].astype(str)

    annual_ratios = ratios[
        ratios["year_text"].str.match(
            r"^(Mar|Jun|Sep|Dec) \d{4}$"
        )
    ].copy()

    annual_ratios["year_num"] = (
        annual_ratios["year_text"]
        .str.extract(r"(\d{4})")[0]
        .astype(int)
    )

    ratios = (
        annual_ratios
        .sort_values(["company_id", "year_num"])
        .drop_duplicates("company_id", keep="last")
    )

    # Select latest market-cap record per company
    market_cap["_year"] = pd.to_numeric(
        market_cap["year"],
        errors="coerce",
    )

    market_cap = (
        market_cap.sort_values(
            ["company_id", "_year"],
            ascending=[True, False],
        )
        .drop_duplicates(
            subset=["company_id"],
            keep="first",
        )
        .drop(columns=["_year"])
    )

    # Select latest P&L record per company
    profit_loss["_period_priority"] = profit_loss["year"].apply(
        period_priority
    )

    profit_loss = (
        profit_loss.sort_values(
            ["company_id", "_period_priority"],
            ascending=[True, False],
        )
        .drop_duplicates(
            subset=["company_id"],
            keep="first",
        )
        .drop(columns=["_period_priority"])
    )

    data = ratios.merge(
        companies,
        on="company_id",
        how="left",
    )

    data = data.merge(
        sectors,
        on="company_id",
        how="left",
    )

    data = data.merge(
        market_cap[
            [
                "company_id",
                "market_cap_crore",
                "pe_ratio",
                "pb_ratio",
                "dividend_yield_pct",
            ]
        ],
        on="company_id",
        how="left",
    )

    data = data.merge(
        profit_loss[
            [
                "company_id",
                "sales",
                "net_profit",
            ]
        ],
        on="company_id",
        how="left",
    )

    return data


def apply_threshold_filters(
    data,
    filters,
):
    """
    Apply configured threshold filters.

    Minimum filters use >=.
    Maximum filters use <=.

    D/E filtering is skipped for Financials companies.
    Debt-free companies always pass ICR minimum filters.
    """

    result = data.copy()

    for filter_name, threshold in filters.items():

        if threshold is None:
            continue

        column = FILTER_COLUMN_MAP.get(filter_name)

        if column is None:
            raise ValueError(
                f"Unsupported screener filter: {filter_name}"
            )

        if column not in result.columns:
            raise KeyError(
                f"Required column missing: {column}"
            )

        if filter_name == "debt_to_equity_max":

            mask = (
                (result["broad_sector"] == "Financials")
                | (
                    result["debt_to_equity"]
                    <= threshold
                )
            )

        elif filter_name == "icr_min":

            mask = (
                (result["icr_label"] == "Debt Free")
                | (
                    result["interest_coverage"]
                    >= threshold
                )
            )

        elif filter_name.endswith("_min"):

            mask = (
                result[column] >= threshold
            )

        elif filter_name.endswith("_max"):

            mask = (
                result[column] <= threshold
            )

        else:
            raise ValueError(
                f"Unsupported filter direction: {filter_name}"
            )

        result = result[mask.fillna(False)]

    return result


def run_screener(
    filters=None,
    config_path=CONFIG_PATH,
    database_path=DATABASE_PATH,
):
    """
    Load data, apply filters, and return sorted results.
    """

    if filters is None:
        filters = load_screener_config(
            config_path
        )

    data = load_latest_financial_data(
        database_path
    )

    result = apply_threshold_filters(
        data,
        filters,
    )

    return result.sort_values(
        "composite_quality_score",
        ascending=False,
    ).reset_index(drop=True)
    
def load_screener_presets(
    config_path=CONFIG_PATH,
):
    """
    Load named preset screener configurations.
    """

    with open(
        config_path,
        "r",
        encoding="utf-8",
    ) as file:

        config = yaml.safe_load(
            file
        ) or {}

    return config.get(
        "presets",
        {}
    ) 
    
    
def run_preset_screener(
    preset_name,
    config_path=CONFIG_PATH,
    database_path=DATABASE_PATH,
):
    """
    Run a named preset screener.
    """

    presets = load_screener_presets(
        config_path
    )

    if preset_name not in presets:

        raise ValueError(
            f"Unknown screener preset: "
            f"{preset_name}"
        )

    return run_screener(
        filters=presets[preset_name],
        config_path=config_path,
        database_path=database_path,
    )       
    
    
    
    