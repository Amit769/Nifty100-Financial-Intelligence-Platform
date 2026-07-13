"""
companies_under5years.py

Find companies having less than 5 years
of financial history.
"""

from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "database" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "companies_under5years.csv"


def main():

    conn = sqlite3.connect(DB_PATH)

    try:

        prices = pd.read_sql(
            """
            SELECT company_id,
                   COUNT(DISTINCT substr(date,1,4)) AS years_available
            FROM stock_prices
            GROUP BY company_id
            """,
            conn
        )

        result = prices[
            prices["years_available"] < 5
        ].sort_values("years_available")

        result.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(result)

        print(f"\nSaved to:\n{OUTPUT_FILE}")

    finally:

        conn.close()


if __name__ == "__main__":
    main()