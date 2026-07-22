import math

from fastapi import APIRouter, HTTPException

from src.screener.engine import (
    load_latest_financial_data,
    apply_threshold_filters,
    load_screener_config,
)


router = APIRouter(
    prefix="/screener",
    tags=["Screener"],
)


@router.get("/")
def get_screener_results():
    """
    Return companies that pass the configured screener filters.
    """

    data = load_latest_financial_data()

    filters = load_screener_config()

    result = apply_threshold_filters(
        data,
        filters,
    )

    records = result.to_dict(
        orient="records"
    )

    clean_records = []

    for record in records:

        clean_record = {}

        for key, value in record.items():

            if isinstance(value, float) and math.isnan(value):
                clean_record[key] = None

            else:
                clean_record[key] = value

        clean_records.append(clean_record)

    return clean_records


@router.get("/{company_id}")
def get_company_screening(company_id: str):
    """
    Return screener result for one company.
    """

    data = load_latest_financial_data()

    filters = load_screener_config()

    result = apply_threshold_filters(
        data,
        filters,
    )

    company = result[
        result["company_id"].str.upper()
        == company_id.upper()
    ]

    if company.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Company '{company_id}' "
                "does not pass the configured screener filters "
                "or does not exist."
            ),
        )

    record = company.iloc[0].to_dict()

    clean_record = {}

    for key, value in record.items():

        if isinstance(value, float) and math.isnan(value):
            clean_record[key] = None

        else:
            clean_record[key] = value

    return clean_record


    
   
    