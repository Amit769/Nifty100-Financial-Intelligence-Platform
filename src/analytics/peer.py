"""
Peer Percentile Analytics
=========================

Computes percentile rankings for financial metrics
within each peer group.
"""

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "nifty100.db"
)


PEER_METRICS = {
    "roe": "return_on_equity_pct",
    "roce": "return_on_capital_employed_pct",
    "net_profit_margin": "net_profit_margin_pct",
    "debt_to_equity": "debt_to_equity",
    "free_cash_flow": "free_cash_flow_cr",
    "pat_cagr_5yr": "pat_cagr_5yr",
    "revenue_cagr_5yr": "revenue_cagr_5yr",
    "eps_cagr_5yr": "eps_cagr_5yr",
    "interest_coverage": "interest_coverage",
    "asset_turnover": "asset_turnover",
}


def load_peer_data(
    database_path=DATABASE_PATH,
):
    """
    Load latest financial data and peer-group assignments.
    """

    connection = sqlite3.connect(
        database_path
    )

    try:

        ratios = pd.read_sql_query(
            """
            SELECT *
            FROM financial_ratios
            """,
            connection,
        )

        peers = pd.read_sql_query(
            """
            SELECT
                peer_group_name,
                company_id,
                is_benchmark
            FROM peer_groups
            """,
            connection,
        )

    finally:
        connection.close()

    ratios["year_num"] = (
        ratios["year"]
        .astype(str)
        .str.extract(
            r"(\d{4})"
        )[0]
        .astype(float)
    )

    ratios = ratios.sort_values(
        [
            "company_id",
            "year_num",
        ]
    )

    # Select the latest non-null value independently
    # for each peer-ranking metric.
    selected_columns = [
        "company_id",
        *PEER_METRICS.values(),
    ]

    latest_values = []

    for company_id, group in ratios.groupby(
        "company_id"
    ):

        record = {
            "company_id": company_id,
        }

        for column in PEER_METRICS.values():

            valid_values = group[
                column
            ].dropna()

            if valid_values.empty:

                record[column] = None

            else:

                record[column] = (
                    valid_values.iloc[-1]
                )

        latest_values.append(
            record
        )

    ratios = pd.DataFrame(
        latest_values
    )

    data = peers.merge(
        ratios,
        on="company_id",
        how="left",
    )

    return data

def calculate_peer_percentiles(
    data,
):
    """
    Calculate percentile ranks within each peer group.

    Higher values are better for all metrics except
    debt_to_equity, where lower values are better.
    """

    percentile_rows = []

    for (
        peer_group_name,
        group,
    ) in data.groupby(
        "peer_group_name"
    ):

        for metric_name, column_name in PEER_METRICS.items():

            metric_data = group[
                [
                    "company_id",
                    column_name,
                ]
            ].copy()

            metric_data = metric_data.dropna(
                subset=[column_name]
            )

            if metric_data.empty:
                continue

            if metric_name == "debt_to_equity":

                metric_data["percentile_rank"] = (
                    metric_data[column_name]
                    .rank(
                        method="average",
                        pct=True,
                        ascending=False,
                    )
                    * 100
                )

            else:

                metric_data["percentile_rank"] = (
                    metric_data[column_name]
                    .rank(
                        method="average",
                        pct=True,
                        ascending=True,
                    )
                    * 100
                )

            for _, row in metric_data.iterrows():

                percentile_rows.append(
                    {
                        "company_id": row[
                            "company_id"
                        ],
                        "peer_group_name": (
                            peer_group_name
                        ),
                        "metric": metric_name,
                        "value": row[
                            column_name
                        ],
                        "percentile_rank": (
                            row[
                                "percentile_rank"
                            ]
                        ),
                    }
                )

    return pd.DataFrame(
        percentile_rows
    )
    
    
def save_peer_percentiles(
    percentiles,
    database_path=DATABASE_PATH,
):
    """
    Save peer percentile rankings to SQLite.
    """

    connection = sqlite3.connect(
        database_path
    )

    try:

        percentiles.to_sql(
            "peer_percentiles",
            connection,
            if_exists="replace",
            index=False,
        )

    finally:

        connection.close()    