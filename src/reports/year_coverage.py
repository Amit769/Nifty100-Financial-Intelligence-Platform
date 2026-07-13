"""
year_coverage.py

Generates year coverage statistics for every company.
"""

from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "database" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "year_coverage.csv"


def detect_year_column(df):
    """
    Detect a year/date column automatically.
    """
    candidates = [
        "year",
        "financial_year",
        "fy",
        "date",
        "period"
    ]

    for col in candidates:
        if col in df.columns:
            return col

    return None


def main():

    conn = sqlite3.connect(DB_PATH)

    financial_tables = [
        "analysis",
        "balancesheet",
        "cashflow",
        "profitandloss",
        "financial_ratios"
    ]

    results = []

    for table in financial_tables:

        try:

            df = pd.read_sql(
                f"SELECT * FROM {table}",
                conn
            )

            if df.empty:
                continue

            year_col = detect_year_column(df)

            if year_col is None:

                results.append({
                    "table": table,
                    "status": "No Year Column",
                    "first_year": None,
                    "last_year": None,
                    "total_years": None
                })

                continue

            df[year_col] = pd.to_numeric(
                df[year_col],
                errors="coerce"
            )

            results.append({

                "table": table,

                "status": "OK",

                "first_year": int(df[year_col].min()),

                "last_year": int(df[year_col].max()),

                "total_years": df[year_col].nunique()

            })

        except Exception as e:

            results.append({

                "table": table,

                "status": str(e),

                "first_year": None,

                "last_year": None,

                "total_years": None

            })

    output = pd.DataFrame(results)

    output.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(output)

    print(f"\nSaved to:\n{OUTPUT_FILE}")

    conn.close()


if __name__ == "__main__":
    main()