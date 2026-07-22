"""
Peer Radar Chart Analytics
==========================

Generates radar charts comparing a company
against its peer-group average.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analytics.peer import (
    load_peer_data,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RADAR_OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "radar_charts"
)


RADAR_METRICS = {
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "NPM": "net_profit_margin_pct",
    "D/E": "debt_to_equity",
    "FCF Score": "free_cash_flow_cr",
    "PAT CAGR 5yr": "pat_cagr_5yr",
    "Revenue CAGR 5yr": "revenue_cagr_5yr",
    "Composite Score": "composite_quality_score",
}


def normalize_metric(
    series,
):
    """
    Normalize a metric to a 0-100 scale.
    """

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            50.0,
            index=series.index,
        )

    return (
        (series - minimum)
        / (maximum - minimum)
        * 100
    )
    
def generate_radar_chart(
    company_id,
    data,
):
    """
    Generate a radar chart comparing one company
    against its peer-group average.
    """

    company = data[
        data["company_id"]
        == company_id
    ]

    if company.empty:
        return None

    company = company.iloc[0]

    peer_group_name = company[
        "peer_group_name"
    ]

    peer_group = data[
        data["peer_group_name"]
        == peer_group_name
    ].copy()

    labels = list(
        RADAR_METRICS.keys()
    )

    company_values = []
    peer_values = []

    for label, column in RADAR_METRICS.items():

        values = peer_group[
            column
        ].dropna()

        if values.empty:
            company_values.append(50.0)
            peer_values.append(50.0)
            continue

        minimum = values.min()
        maximum = values.max()

        if minimum == maximum:

            company_score = 50.0
            peer_score = 50.0

        else:

            company_score = (
                (
                    company[column]
                    - minimum
                )
                / (
                    maximum
                    - minimum
                )
                * 100
            )

            peer_score = (
                (
                    values.mean()
                    - minimum
                )
                / (
                    maximum
                    - minimum
                )
                * 100
            )

        if label == "D/E":

            company_score = (
                100
                - company_score
            )

            peer_score = (
                100
                - peer_score
            )

        company_values.append(
            company_score
        )

        peer_values.append(
            peer_score
        )

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False,
    )

    company_values += (
        company_values[:1]
    )

    peer_values += (
        peer_values[:1]
    )

    angles = np.concatenate(
        [
            angles,
            angles[:1],
        ]
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw={
            "polar": True,
        },
    )

    ax.plot(
        angles,
        company_values,
        linewidth=2,
        label=company_id,
    )

    ax.fill(
        angles,
        company_values,
        alpha=0.25,
    )

    ax.plot(
        angles,
        peer_values,
        linestyle="--",
        linewidth=2,
        label="Peer Average",
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels,
        fontsize=9,
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.set_title(
        f"{company_id} — {peer_group_name}",
        pad=20,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(
            1.25,
            1.10,
        ),
    )

    RADAR_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        RADAR_OUTPUT_DIR
        / f"{company_id}_radar.png"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
    )

    plt.close()

    return output_path   

def generate_all_radar_charts(
    data,
):
    """
    Generate radar charts for every company
    assigned to a peer group.
    """

    generated_files = []

    company_ids = (
        data["company_id"]
        .dropna()
        .unique()
    )

    for company_id in company_ids:

        output_path = (
            generate_radar_chart(
                company_id,
                data,
            )
        )

        if output_path is not None:
            generated_files.append(
                output_path
            )

    return generated_files 

def load_all_financial_data():
    """
    Load all companies with their optional peer-group assignment.
    """

    data = load_peer_data()

    peer_company_ids = set(
        data["company_id"]
    )

    # Load all financial data through the existing
    # peer loader's underlying database logic.
    from src.analytics.peer import DATABASE_PATH
    import sqlite3

    connection = sqlite3.connect(
        DATABASE_PATH
    )

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
            SELECT id AS company_id
            FROM companies
            """,
            connection,
        )

    finally:

        connection.close()

    ratios["year_num"] = (
        ratios["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .astype(float)
    )

    ratios = (
        ratios
        .sort_values(
            [
                "company_id",
                "year_num",
            ]
        )
        .drop_duplicates(
            "company_id",
            keep="last",
        )
    )

    all_data = companies.merge(
        ratios,
        on="company_id",
        how="left",
    )

    peer_assignments = data[
        [
            "company_id",
            "peer_group_name",
        ]
    ].drop_duplicates(
        "company_id"
    )

    all_data = all_data.merge(
        peer_assignments,
        on="company_id",
        how="left",
    )

    return all_data

def generate_standalone_radar_chart(
    company_id,
    data,
):
    """
    Generate a standalone radar chart for a company
    without a peer group.

    The reference is the Nifty 100 average.
    """

    company = data[
        data["company_id"] == company_id
    ]

    if company.empty:
        return None

    company = company.iloc[0]

    labels = list(RADAR_METRICS.keys())

    company_values = []
    nifty_average_values = []

    for label, column in RADAR_METRICS.items():

        all_values = data[column].dropna()

        if all_values.empty:
            company_values.append(50.0)
            nifty_average_values.append(50.0)
            continue

        minimum = all_values.min()
        maximum = all_values.max()

        if minimum == maximum:
            company_score = 50.0
            average_score = 50.0

        else:
            company_score = (
                (company[column] - minimum)
                / (maximum - minimum)
                * 100
            )

            average_score = (
                (all_values.mean() - minimum)
                / (maximum - minimum)
                * 100
            )

        if label == "D/E":
            company_score = 100 - company_score
            average_score = 100 - average_score

        company_values.append(company_score)
        nifty_average_values.append(average_score)

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False,
    )

    company_values += company_values[:1]
    nifty_average_values += nifty_average_values[:1]

    angles = np.concatenate(
        [angles, angles[:1]]
    )

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw={"polar": True},
    )

    ax.plot(
        angles,
        company_values,
        linewidth=2,
        label=company_id,
    )

    ax.fill(
        angles,
        company_values,
        alpha=0.25,
    )

    ax.plot(
        angles,
        nifty_average_values,
        linestyle="--",
        linewidth=2,
        label="Nifty 100 Average",
    )

    ax.set_xticks(angles[:-1])

    ax.set_xticklabels(
        labels,
        fontsize=9,
    )

    ax.set_ylim(0, 100)

    ax.set_title(
        f"{company_id} — Nifty 100 Benchmark",
        pad=20,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.25, 1.10),
    )

    RADAR_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        RADAR_OUTPUT_DIR
        / f"{company_id}_radar.png"
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
    )

    plt.close()

    return output_path

def generate_all_company_radar_charts(
    data,
):
    """
    Generate the correct radar chart for all companies.

    Companies with a peer group:
        Company vs Peer Average

    Companies without a peer group:
        Company vs Nifty 100 Average
    """

    generated_files = []

    for _, company in data.iterrows():

        company_id = company["company_id"]

        if pd.notna(
            company["peer_group_name"]
        ):

            output_path = (
                generate_radar_chart(
                    company_id,
                    data[
                        data[
                            "peer_group_name"
                        ].notna()
                    ],
                )
            )

        else:

            output_path = (
                generate_standalone_radar_chart(
                    company_id,
                    data,
                )
            )

        if output_path is not None:

            generated_files.append(
                output_path
            )

    return generated_files