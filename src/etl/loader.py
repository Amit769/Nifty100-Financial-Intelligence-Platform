"""
loader.py

Generic Excel loader for the Nifty100 Financial Intelligence Platform.

Responsibilities:
- Read Excel files
- Apply correct header row
- Normalize column names
- Validate required columns
- Return cleaned DataFrame
"""

from pathlib import Path
import re
import pandas as pd

from src.etl.column_mapper import WORKBOOK_CONFIG


class ExcelLoader:
    """Generic Excel Loader"""

    def __init__(self, raw_data_dir):
        self.raw_data_dir = Path(raw_data_dir)

    @staticmethod
    def normalize_column_name(column):
        """
        Convert Excel column names to database-friendly format.

        Example:
        'Company Name' -> company_name
        'ROCE %' -> roce_percentage
        """

        column = str(column).strip().lower()

        replacements = {
            "%": "percentage",
            "&": "and",
            "/": "_",
            "-": "_",
            "(": "",
            ")": "",
            ".": "",
            " ": "_"
        }

        for old, new in replacements.items():
            column = column.replace(old, new)

        column = re.sub(r"_+", "_", column)

        return column.strip("_")

    def load_workbook(self, workbook_name):
        """
        Load one workbook according to WORKBOOK_CONFIG.
        """

        if workbook_name not in WORKBOOK_CONFIG:
            raise ValueError(f"{workbook_name} not configured.")

        config = WORKBOOK_CONFIG[workbook_name]

        file_path = self.raw_data_dir / workbook_name

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        df = pd.read_excel(
            file_path,
            sheet_name=config["sheet"],
            header=config["header"]
        )

        df.columns = [
            self.normalize_column_name(col)
            for col in df.columns
        ]

        mapping = config.get("column_mapping", {})

        if mapping:
            df.rename(columns=mapping, inplace=True)

        required = config.get("required_columns", [])

        missing = [
            col
            for col in required
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"{workbook_name} missing columns: {missing}"
            )

        df = df.dropna(how="all")

        df.reset_index(drop=True, inplace=True)
        # Clean all string columns
        for col in df.select_dtypes(include="object").columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": None})
            )

        return df

    def load_all_workbooks(self):
        """
        Load every workbook defined in WORKBOOK_CONFIG.

        Returns:
            dict[str, pd.DataFrame]
        """

        datasets = {}

        for workbook in WORKBOOK_CONFIG:

            print(f"Loading {workbook}...")

            datasets[workbook] = self.load_workbook(workbook)

        return datasets