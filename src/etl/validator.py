"""
validator.py

Runs Data Quality (DQ) validation rules
and generates a validation report.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from .validation_rules import (
    check_duplicates,
    check_negative_values,
    check_nulls,
    check_required_columns,
    check_year_format,
)


class DataValidator:
    """
    Executes Data Quality validation rules.
    """

    def __init__(self):
        self.failures = []

    def _add_failure(
        self,
        rule_id: str,
        severity: str,
        table: str,
        row: int,
        message: str,
    ):
        self.failures.append(
            {
                "rule_id": rule_id,
                "severity": severity,
                "table": table,
                "row": row,
                "message": message,
            }
        )

    def validate(
        self,
        df: pd.DataFrame,
        table_name: str,
        required_columns: list[str],
        pk_columns: list[str],
        numeric_columns: list[str],
        year_column: str = "year",
    ):
        """
        Execute validation rules.
        """

        # DQ-01 Required Columns
        missing = check_required_columns(df, required_columns)

        for col in missing:
            self._add_failure(
                "DQ-01",
                "CRITICAL",
                table_name,
                -1,
                f"Missing required column: {col}",
            )
        if missing:
         return

        # DQ-02 NULL values
        if all(c in df.columns for c in required_columns):

            null_rows = check_nulls(df, required_columns)

            for idx in null_rows.index:
                self._add_failure(
                    "DQ-02",
                    "CRITICAL",
                    table_name,
                    int(idx),
                    "Mandatory field contains NULL",
                )

        # DQ-03 Duplicate PK
        duplicates = check_duplicates(df, pk_columns)

        for idx in duplicates.index:
            self._add_failure(
                "DQ-03",
                "CRITICAL",
                table_name,
                int(idx),
                "Duplicate primary key",
            )

        # DQ-04 Invalid year
        invalid_years = check_year_format(df, year_column)

        for idx in invalid_years.index:
            self._add_failure(
                "DQ-04",
                "WARNING",
                table_name,
                int(idx),
                "Invalid year format",
            )

        # DQ-05 Negative numeric values
        negatives = check_negative_values(df, numeric_columns)

        for idx in negatives.index:
            self._add_failure(
                "DQ-05",
                "WARNING",
                table_name,
                int(idx),
                "Negative numeric value detected",
            )

    def save_report(
        self,
        filepath: str | Path = "output/validation_failures.csv",
    ):
        """
        Save validation report.
        """

        filepath = Path(filepath)

        filepath.parent.mkdir(parents=True, exist_ok=True)

        pd.DataFrame(self.failures).to_csv(
            filepath,
            index=False,
        )

    def summary(self):
        """
        Print validation summary.
        """

        if not self.failures:
            print("✅ No validation failures found.")
            return

        report = pd.DataFrame(self.failures)

        print(report.groupby(["severity"]).size())