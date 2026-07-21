"""
Day 13 — Ratio Edge Case Checker

Cross-checks computed ROCE and ROE values against
source values stored in the companies table.

Anomalies:
- ROCE difference > 5 percentage points
- ROE difference > 5 percentage points

Financials sector companies are included in the analysis,
but their high leverage warning is intentionally suppressed.
"""

import sqlite3
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "database" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_PATH = OUTPUT_DIR / "ratio_edge_cases.log"


def classify_anomaly(
    computed_value,
    source_value,
    difference,
):
    """
    Classify an anomaly using practical heuristics.
    """

    if computed_value is None or source_value is None:
        return "DATA_SOURCE_ISSUE"

    if abs(difference) > 20:
        return "DATA_SOURCE_ISSUE"

    if abs(difference) > 5:
        return "VERSION_DIFFERENCE"

    return "FORMULA_DISCREPANCY"


def run_edge_case_check():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    rows = connection.execute(
        """
        SELECT
            fr.company_id,
            c.company_name,
            s.broad_sector,

            fr.year,

            fr.return_on_capital_employed_pct
                AS computed_roce,

            c.roce_percentage
                AS source_roce,

            fr.return_on_equity_pct
                AS computed_roe,

            c.roe_percentage
                AS source_roe

        FROM financial_ratios fr

        JOIN companies c
            ON c.id = fr.company_id

        LEFT JOIN sectors s
            ON s.company_id = fr.company_id

        WHERE
            (
                c.roce_percentage IS NOT NULL
                AND fr.return_on_capital_employed_pct IS NOT NULL
                AND ABS(
                    fr.return_on_capital_employed_pct
                    - c.roce_percentage
                ) > 5
            )

            OR

            (
                c.roe_percentage IS NOT NULL
                AND fr.return_on_equity_pct IS NOT NULL
                AND ABS(
                    fr.return_on_equity_pct
                    - c.roe_percentage
                ) > 5
            )

        ORDER BY fr.company_id, fr.year
        """
    ).fetchall()

    with open(LOG_PATH, "w", encoding="utf-8") as log:

        log.write("RATIO EDGE CASE LOG\n")
        log.write("=" * 80 + "\n")
        log.write(
            f"Generated: {datetime.now().isoformat()}\n"
        )
        log.write(
            "ROCE/ROE anomaly threshold: > 5 percentage points\n"
        )
        log.write("=" * 80 + "\n\n"
        )

        if not rows:

            log.write(
                "No ROCE or ROE anomalies detected.\n"
            )

        else:

            for row in rows:

                (
                    company_id,
                    company_name,
                    broad_sector,
                    year,
                    computed_roce,
                    source_roce,
                    computed_roe,
                    source_roe,
                ) = row

                log.write(
                    f"Company: {company_id} | "
                    f"{company_name}\n"
                )

                log.write(
                    f"Sector: {broad_sector}\n"
                )

                log.write(
                    f"Year: {year}\n"
                )

                if (
                    computed_roce is not None
                    and source_roce is not None
                ):

                    roce_difference = (
                        computed_roce
                        - source_roce
                    )

                    if abs(roce_difference) > 5:

                        category = classify_anomaly(
                            computed_roce,
                            source_roce,
                            roce_difference,
                        )

                        log.write(
                            f"ROCE | "
                            f"Computed: {computed_roce:.2f} | "
                            f"Source: {source_roce:.2f} | "
                            f"Difference: "
                            f"{roce_difference:.2f} | "
                            f"Category: {category}\n"
                        )

                if (
                    computed_roe is not None
                    and source_roe is not None
                ):

                    roe_difference = (
                        computed_roe
                        - source_roe
                    )

                    if abs(roe_difference) > 5:

                        category = classify_anomaly(
                            computed_roe,
                            source_roe,
                            roe_difference,
                        )

                        log.write(
                            f"ROE | "
                            f"Computed: {computed_roe:.2f} | "
                            f"Source: {source_roe:.2f} | "
                            f"Difference: "
                            f"{roe_difference:.2f} | "
                            f"Category: {category}\n"
                        )

                log.write("-" * 80 + "\n")

    connection.close()

    print(
        f"Edge-case log generated:\n{LOG_PATH}"
    )

    print(
        f"Anomalous company-year records: {len(rows)}"
    )


if __name__ == "__main__":

    run_edge_case_check()