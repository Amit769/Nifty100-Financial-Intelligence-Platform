"""
validation_failures.py

Generates a Data Quality report for the
Nifty100 Financial Intelligence Platform.
"""

from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "database" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "validation_failures.csv"


def add_issue(results, severity, table, issue, company_id=""):

    results.append({
        "severity": severity,
        "table": table,
        "issue": issue,
        "company_id": company_id
    })


def main():

    conn = sqlite3.connect(DB_PATH)

    results = []

    # -----------------------------
    # Companies
    # -----------------------------

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    # Duplicate IDs
    duplicates = companies[
        companies["id"].duplicated()
    ]

    for _, row in duplicates.iterrows():

        add_issue(
            results,
            "HIGH",
            "companies",
            "Duplicate company id",
            row["id"]
        )

    # Missing IDs
    missing = companies[
        companies["id"].isna()
    ]

    for _ in range(len(missing)):

        add_issue(
            results,
            "HIGH",
            "companies",
            "Missing company id"
        )

    company_ids = set(
        companies["id"].dropna()
    )

    # -----------------------------
    # Child tables
    # -----------------------------

    child_tables = [
        "analysis",
        "balancesheet",
        "cashflow",
        "profitandloss",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "prosandcons",
        "sectors",
        "stock_prices",
        "documents"
    ]

    for table in child_tables:

        try:

            df = pd.read_sql(
                f"SELECT * FROM {table}",
                conn
            )

        except Exception:

            add_issue(
                results,
                "HIGH",
                table,
                "Table not found"
            )

            continue

        # Missing company_id column

        if "company_id" not in df.columns:

            add_issue(
                results,
                "HIGH",
                table,
                "company_id column missing"
            )

            continue

        # Missing company_id values

        missing_company = df[
            df["company_id"].isna()
        ]

        for _ in range(len(missing_company)):

            add_issue(
                results,
                "HIGH",
                table,
                "Missing company_id"
            )

        # Invalid foreign keys

        invalid = df[
            ~df["company_id"].isin(company_ids)
        ]

        for _, row in invalid.iterrows():

            add_issue(
                results,
                "HIGH",
                table,
                "Company not found in companies table",
                row["company_id"]
            )

        # Missing dates

        if "date" in df.columns:

            missing_dates = df[
                df["date"].isna()
            ]

            for _, row in missing_dates.iterrows():

                add_issue(
                    results,
                    "MEDIUM",
                    table,
                    "Missing date",
                    row["company_id"]
                )

    report = pd.DataFrame(results)

    report.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(report)

    print(f"\nValidation report saved to:\n{OUTPUT_FILE}")

    conn.close()


if __name__ == "__main__":
    main()