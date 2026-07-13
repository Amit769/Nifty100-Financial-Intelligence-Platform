"""
manual_review.py

Performs a manual data quality review by randomly selecting
5 companies and checking whether related records exist
across all tables.
"""

from pathlib import Path
import sqlite3
import random
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "database" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "manual_review.csv"


def table_has_company(cursor, table_name, company_id):
    """
    Returns True if company exists in the table.
    """

    # companies table uses id
    if table_name == "companies":
        cursor.execute(
            "SELECT COUNT(*) FROM companies WHERE id=?",
            (company_id,)
        )
    else:
        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE company_id=?",
            (company_id,)
        )

    return cursor.fetchone()[0] > 0


def main():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM companies")
    company_ids = [row[0] for row in cursor.fetchall()]

    sample = random.sample(company_ids, min(5, len(company_ids)))

    tables = [
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

    results = []

    for company in sample:

        row = {"company_id": company}

        for table in tables:

            row[table] = (
                "YES"
                if table_has_company(cursor, table, company)
                else "NO"
            )

        results.append(row)

    df = pd.DataFrame(results)

    df.to_csv(OUTPUT_FILE, index=False)

    print(df)

    print(f"\nManual review saved to:\n{OUTPUT_FILE}")

    conn.close()


if __name__ == "__main__":
    main()