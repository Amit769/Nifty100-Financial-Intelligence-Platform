"""
validation_rules.py

Data Quality (DQ) rules for ETL validation.
"""

from __future__ import annotations

import pandas as pd


def check_required_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    """
    Return missing required columns.
    """
    return [col for col in required if col not in df.columns]


def check_nulls(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Rows with NULL values in required columns.
    """
    return df[df[columns].isnull().any(axis=1)]


def check_duplicates(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    """
    Duplicate primary key rows.
    """
    return df[df.duplicated(subset=subset, keep=False)]


def check_negative_values(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Detect rows containing negative values in the specified columns.
    """

    valid_columns = [col for col in columns if col in df.columns]

    if not valid_columns:
        return pd.DataFrame(columns=df.columns)

    mask = (df[valid_columns] < 0).any(axis=1)

    return df[mask]


def check_year_format(df: pd.DataFrame, year_column: str) -> pd.DataFrame:
    """
    Detect invalid years.
    """

    if year_column not in df.columns:
        return pd.DataFrame()

    pattern = r"^\d{4}(-\d{2})?$"

    return df[
        ~df[year_column]
        .astype(str)
        .str.match(pattern, na=False)
    ]