"""
Ratio Engine
============

Populates the financial_ratios table from the authoritative
92-company master universe and available financial statements.
"""

from pathlib import Path
import sqlite3
from collections import defaultdict

from src.analytics.ratios import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    calculate_roe,
    calculate_roce,
    calculate_roa,
    calculate_debt_to_equity,
    calculate_high_leverage_flag,
    calculate_interest_coverage,
    get_icr_label,
    calculate_icr_warning,
    calculate_net_debt,
    calculate_asset_turnover,
)

from src.analytics.cagr import calculate_window_cagr

from src.analytics.cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_cfo_quality_score,
    calculate_capex_intensity,
    calculate_fcf_conversion_rate,
    classify_capital_allocation,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "database" / "nifty100.db"


def safe_value(value):
    """
    Convert database NULL values to Python None.
    """
    return value


def load_source_data(connection):
    """
    Load all source tables into dictionaries keyed by
    (company_id, year).
    """

    companies = {
    row[0]: {
        "company_name": row[1],
        "book_value": row[2],
    }
    for row in connection.execute(
        """
        SELECT id, company_name, book_value
        FROM companies
        """
    ).fetchall()
}

    profit_loss = {}
    for row in connection.execute(
        """
        SELECT
            company_id,
            year,
            sales,
            operating_profit,
            opm_percentage,
            other_income,
            interest,
            net_profit,
            eps,
            dividend_payout
        FROM profitandloss
        """
    ).fetchall():

        key = (row[0], row[1])

        profit_loss[key] = {
            "sales": row[2],
            "operating_profit": row[3],
            "opm_percentage": row[4],
            "other_income": row[5],
            "interest": row[6],
            "net_profit": row[7],
            "eps": row[8],
            "dividend_payout": row[9],
        }

    balance_sheet = {}
    for row in connection.execute(
        """
        SELECT
            company_id,
            year,
            equity_capital,
            reserves,
            borrowings,
            investments,
            total_assets
        FROM balancesheet
        """
    ).fetchall():

        key = (row[0], row[1])

        balance_sheet[key] = {
            "equity_capital": row[2],
            "reserves": row[3],
            "borrowings": row[4],
            "investments": row[5],
            "total_assets": row[6],
        }

    cash_flow = {}
    for row in connection.execute(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity
        FROM cashflow
        """
    ).fetchall():

        key = (row[0], row[1])

        cash_flow[key] = {
            "operating_activity": row[2],
            "investing_activity": row[3],
            "financing_activity": row[4],
        }

    return companies, profit_loss, balance_sheet, cash_flow


def get_broad_sector(connection, company_id):
    """
    Return the broad sector for a company.

    The sectors table is used if a broad_sector column exists.
    """
    columns = [
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(sectors)"
        ).fetchall()
    ]

    if "broad_sector" not in columns:
        return None

    row = connection.execute(
        """
        SELECT broad_sector
        FROM sectors
        WHERE company_id = ?
        LIMIT 1
        """,
        (company_id,),
    ).fetchone()

    return row[0] if row else None


def build_time_series(source_data, company_id, value_key):
    """
    Build a year-value mapping for CAGR calculations.
    """

    values = {}

    for (cid, year), data in source_data.items():

        if cid != company_id:
            continue

        try:
            numeric_year = int(str(year).split()[-1])
        except (ValueError, TypeError):
            continue

        value = data.get(value_key)

        if value is not None:
            values[numeric_year] = value

    return values


def calculate_cagr_metrics(
    company_id,
    profit_loss,
):
    """
    Calculate 3-year, 5-year, and 10-year CAGR metrics
    for revenue, PAT, and EPS.
    """

    revenue_series = build_time_series(
        profit_loss,
        company_id,
        "sales",
    )

    pat_series = build_time_series(
        profit_loss,
        company_id,
        "net_profit",
    )

    eps_series = build_time_series(
        profit_loss,
        company_id,
        "eps",
    )

    result = {}

    for metric_name, series in [
        ("revenue", revenue_series),
        ("pat", pat_series),
        ("eps", eps_series),
    ]:

        for years in [3, 5, 10]:

            cagr = calculate_window_cagr(
                values=series,
                years=years,
            )

            result[f"{metric_name}_cagr_{years}yr"] = cagr["value"]
            result[f"{metric_name}_cagr_{years}yr_flag"] = cagr["flag"]

    return result


def populate_financial_ratios():
    """
    Calculate and populate financial_ratios.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    try:

        companies, profit_loss, balance_sheet, cash_flow = (
            load_source_data(connection)
        )

        # Clear any previous ratio calculations
        connection.execute(
            "DELETE FROM financial_ratios"
        )

        # Use only the authoritative company universe
        company_ids = set(companies.keys())

        all_keys = set()

        for source in [
            profit_loss,
            balance_sheet,
            cash_flow,
        ]:

            all_keys.update(
                key
                for key in source.keys()
                if key[0] in company_ids
            )

        rows = []

        for company_id, year in sorted(all_keys):

            pnl = profit_loss.get(
                (company_id, year),
                {},
            )

            bs = balance_sheet.get(
                (company_id, year),
                {},
            )

            cf = cash_flow.get(
                (company_id, year),
                {},
            )

            sales = pnl.get("sales")
            net_profit = pnl.get("net_profit")
            operating_profit = pnl.get("operating_profit")
            other_income = pnl.get("other_income")
            interest = pnl.get("interest")
            eps = pnl.get("eps")
            dividend_payout = pnl.get("dividend_payout")

            equity_capital = bs.get("equity_capital")
            reserves = bs.get("reserves")
            borrowings = bs.get("borrowings")
            investments = bs.get("investments")
            total_assets = bs.get("total_assets")

            operating_activity = cf.get(
                "operating_activity"
            )

            investing_activity = cf.get(
                "investing_activity"
            )

            financing_activity = cf.get(
                "financing_activity"
            )

            sector = get_broad_sector(
                connection,
                company_id,
            )

            # Profitability
            npm = calculate_net_profit_margin(
                net_profit,
                sales,
            )

            opm = calculate_operating_profit_margin(
                operating_profit,
                sales,
            )

            roe = calculate_roe(
                net_profit,
                equity_capital,
                reserves,
            )

            roce = calculate_roce(
                operating_profit,
                equity_capital,
                reserves,
                borrowings,
            )

            roa = calculate_roa(
                net_profit,
                total_assets,
            )

            # Leverage
            de = calculate_debt_to_equity(
                borrowings,
                equity_capital,
                reserves,
            )

            high_leverage = calculate_high_leverage_flag(
                de,
                sector,
            )

            icr = calculate_interest_coverage(
                operating_profit,
                other_income,
                interest,
            )

            icr_label = get_icr_label(icr)

            icr_warning = calculate_icr_warning(icr)

            net_debt = calculate_net_debt(
                borrowings,
                investments,
            )

            asset_turnover = calculate_asset_turnover(
                sales,
                total_assets,
            )

            # Cash Flow
            fcf = calculate_free_cash_flow(
                operating_activity,
                investing_activity,
            )

            capex = (
                abs(investing_activity)
                if investing_activity is not None
                else None
            )

            capex_result = calculate_capex_intensity(
                investing_activity,
                sales,
            )

            cfo_quality = calculate_cfo_quality_score(
                [operating_activity],
                [net_profit],
            )

            fcf_conversion = calculate_fcf_conversion_rate(
                fcf,
                operating_profit,
            )

            cfo_pat_ratio = None

            if (
                operating_activity is not None
                and net_profit is not None
                and net_profit != 0
            ):
                cfo_pat_ratio = (
                    operating_activity / net_profit
                )

            capital_pattern = classify_capital_allocation(
                operating_activity,
                investing_activity,
                financing_activity,
                cfo_pat_ratio,
            )

            # CAGR
            cagr = calculate_cagr_metrics(
                company_id,
                profit_loss,
            )
            book_value_per_share = companies[company_id]["book_value"]
            composite_quality_score = (
    calculate_composite_quality_score(
        roe=roe,
        roce=roce,
        npm=npm,
        revenue_cagr_5yr=cagr.get(
            "revenue_cagr_5yr"
        ),
        pat_cagr_5yr=cagr.get(
            "pat_cagr_5yr"
        ),
        cfo_quality_score=(
            cfo_quality["score"]
        ),
        debt_to_equity=de,
    )
)

            row = {
                "company_id": company_id,
                "year": year,

                "net_profit_margin_pct": npm,
                "operating_profit_margin_pct": opm,
                "return_on_equity_pct": roe,
                "return_on_capital_employed_pct": roce,
                "return_on_assets_pct": roa,

                "debt_to_equity": de,
                "high_leverage_flag": high_leverage,
                "interest_coverage": icr,
                "icr_label": icr_label,
                "icr_warning_flag": icr_warning,
                "net_debt_cr": net_debt,
                "asset_turnover": asset_turnover,

                "free_cash_flow_cr": fcf,
                "capex_cr": capex,
                "capex_intensity_pct": capex_result["percentage"],
                "cfo_quality_score": cfo_quality["score"],
                "fcf_conversion_rate_pct": fcf_conversion,

                "earnings_per_share": eps,
                "book_value_per_share": book_value_per_share,
                "dividend_payout_ratio_pct": dividend_payout,

                "total_debt_cr": borrowings,
                "cash_from_operations_cr": operating_activity,

                **cagr,

                "composite_quality_score": ( composite_quality_score ),
            }

            rows.append(row)

        columns = list(rows[0].keys())

        placeholders = ", ".join(
            ["?"] * len(columns)
        )

        column_sql = ", ".join(columns)

        insert_sql = f"""
            INSERT INTO financial_ratios
            ({column_sql})
            VALUES ({placeholders})
        """

        connection.executemany(
            insert_sql,
            [
                tuple(row[column] for column in columns)
                for row in rows
            ],
        )

        connection.commit()

        print(
            f"Inserted {len(rows)} financial ratio rows."
        )

    finally:

        connection.close()


def normalize_score(value, minimum, maximum):
    """
    Normalize a value to a 0-100 scale.
    """
    if value is None:
        return None

    if maximum == minimum:
        return 0.0

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100

    return max(0.0, min(100.0, score))


def calculate_composite_quality_score(
    roe,
    roce,
    npm,
    revenue_cagr_5yr,
    pat_cagr_5yr,
    cfo_quality_score,
    debt_to_equity,
):
    """
    Calculate weighted Composite Quality Score on a 0-100 scale.
    """

    components = []

    if roe is not None:
        components.append(
            (
                normalize_score(roe, 0, 20),
                0.20,
            )
        )

    if roce is not None:
        components.append(
            (
                normalize_score(roce, 0, 20),
                0.20,
            )
        )

    if npm is not None:
        components.append(
            (
                normalize_score(npm, 0, 20),
                0.15,
            )
        )

    if revenue_cagr_5yr is not None:
        components.append(
            (
                normalize_score(
                    revenue_cagr_5yr,
                    0,
                    15,
                ),
                0.15,
            )
        )

    if pat_cagr_5yr is not None:
        components.append(
            (
                normalize_score(
                    pat_cagr_5yr,
                    0,
                    15,
                ),
                0.15,
            )
        )

    if cfo_quality_score is not None:
        components.append(
            (
                normalize_score(
                    cfo_quality_score,
                    0,
                    1,
                ),
                0.10,
            )
        )

    if debt_to_equity is not None:
        leverage_score = normalize_score(
            5 - debt_to_equity,
            0,
            5,
        )

        components.append(
            (
                leverage_score,
                0.05,
            )
        )

    if not components:
        return None

    weighted_score = sum(
        score * weight
        for score, weight in components
    )

    total_weight = sum(
        weight
        for _, weight in components
    )

    return weighted_score / total_weight