"""
etl_pipeline.py

Main ETL Pipeline

Steps
------
1. Recreate SQLite database
2. Create schema
3. Load Excel workbooks
4. Insert into SQLite
5. Generate audit report
"""

from pathlib import Path
import sqlite3
import pandas as pd

from src.etl.loader import ExcelLoader
from src.etl.column_mapper import WORKBOOK_CONFIG

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "nifty100.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
AUDIT_PATH = PROJECT_ROOT / "data" / "processed" / "load_audit.csv"


class ETLPipeline:

    def __init__(self):

        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)

        self.loader = ExcelLoader(RAW_DATA_DIR)

        self.connection = None
        self.audit = []

    # --------------------------------------------------

    def connect_database(self):

        if self.connection:
            self.connection.close()

        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()

        self.connection = sqlite3.connect(DATABASE_PATH)

    # --------------------------------------------------

    def create_schema(self):

        print("Creating database schema...")

        self.connect_database()

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = f.read()

        self.connection.executescript(schema)
        self.connection.commit()

    # --------------------------------------------------

    def load_data(self):

        datasets = self.loader.load_all_workbooks()

        for workbook, dataframe in datasets.items():

            table = WORKBOOK_CONFIG[workbook]["table"]

            try:

                dataframe.to_sql(
                    table,
                    self.connection,
                    if_exists="append",
                    index=False
                )

                self.audit.append({
                    "table": table,
                    "status": "SUCCESS",
                    "rows_loaded": len(dataframe),
                    "message": ""
                })

                print(f"Loaded {table}: {len(dataframe)} rows")

            except Exception as error:
                import traceback

                self.audit.append({
                    "table": table,
                    "status": "FAILED",
                    "rows_loaded": 0,
                    "message": str(error)
                })

                print("\n" + "=" * 60)
                print(f"FAILED TABLE : {table}")
                print("=" * 60)
                traceback.print_exc()
                print("=" * 60)

        self.connection.commit()

    # --------------------------------------------------

    def export_audit(self):

        audit_df = pd.DataFrame(self.audit)

        audit_df.to_csv(
            AUDIT_PATH,
            index=False
        )

        print(f"\nAudit saved to:\n{AUDIT_PATH}")

    # --------------------------------------------------

    def close(self):

        if self.connection:
            self.connection.close()

    # --------------------------------------------------

    def run(self):

        try:

            self.create_schema()

            self.load_data()

            self.export_audit()

            print("\nETL Completed Successfully.")

        finally:

            self.close()


if __name__ == "__main__":

    ETLPipeline().run()