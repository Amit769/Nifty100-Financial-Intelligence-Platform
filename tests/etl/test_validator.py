"""
Unit tests for validator.py
"""

import pandas as pd

from src.etl.validator import DataValidator


def test_valid_dataframe():
    """
    Valid dataframe should produce no failures.
    """

    df = pd.DataFrame(
        {
            "company_id": ["TCS", "INFY"],
            "company_name": ["TCS Ltd", "Infosys"],
            "year": ["2023", "2024"],
            "sales": [1000, 2000],
        }
    )

    validator = DataValidator()

    validator.validate(
        df=df,
        table_name="companies",
        required_columns=["company_id", "company_name"],
        pk_columns=["company_id"],
        numeric_columns=["sales"],
    )

    assert len(validator.failures) == 0


def test_duplicate_primary_key():

    df = pd.DataFrame(
        {
            "company_id": ["TCS", "TCS"],
            "company_name": ["TCS", "TCS"],
            "year": ["2023", "2023"],
            "sales": [1000, 2000],
        }
    )

    validator = DataValidator()

    validator.validate(
        df=df,
        table_name="companies",
        required_columns=["company_id"],
        pk_columns=["company_id"],
        numeric_columns=["sales"],
    )

    assert any(
        f["rule_id"] == "DQ-03"
        for f in validator.failures
    )


def test_missing_required_column():

    df = pd.DataFrame(
        {
            "company_id": ["TCS"]
        }
    )

    validator = DataValidator()

    validator.validate(
        df=df,
        table_name="companies",
        required_columns=[
            "company_id",
            "company_name",
        ],
        pk_columns=["company_id"],
        numeric_columns=[],
    )

    assert any(
        f["rule_id"] == "DQ-01"
        for f in validator.failures
    )


def test_invalid_year():

    df = pd.DataFrame(
        {
            "company_id": ["TCS"],
            "company_name": ["TCS"],
            "year": ["ABC"],
            "sales": [100],
        }
    )

    validator = DataValidator()

    validator.validate(
        df=df,
        table_name="companies",
        required_columns=["company_id"],
        pk_columns=["company_id"],
        numeric_columns=["sales"],
    )

    assert any(
        f["rule_id"] == "DQ-04"
        for f in validator.failures
    )


def test_negative_sales():

    df = pd.DataFrame(
        {
            "company_id": ["TCS"],
            "company_name": ["TCS"],
            "year": ["2023"],
            "sales": [-500],
        }
    )

    validator = DataValidator()

    validator.validate(
        df=df,
        table_name="companies",
        required_columns=["company_id"],
        pk_columns=["company_id"],
        numeric_columns=["sales"],
    )

    assert any(
        f["rule_id"] == "DQ-05"
        for f in validator.failures
    )