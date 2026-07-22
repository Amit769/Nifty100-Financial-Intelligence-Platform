import math
from fastapi import APIRouter, HTTPException

from src.screener.engine import load_latest_financial_data


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get("/")
def get_companies():
    """
    Return all companies in the Nifty 100 universe.
    """

    data = load_latest_financial_data()

    companies = (
        data[
            [
                "company_id",
                "company_name",
                "broad_sector",
                "sub_sector",
            ]
        ]
        .drop_duplicates("company_id")
        .sort_values("company_id")
    )

    return companies.to_dict(
        orient="records"
    )


@router.get("/{company_id}")
def get_company_detail(company_id: str):
    """
    Return detailed financial data for one company.
    """

    data = load_latest_financial_data()

    company = data[
        data["company_id"].str.upper()
        == company_id.upper()
    ]

    if company.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_id}' not found",
        )

    record = company.iloc[0].to_dict()

    clean_record = {}

    for key, value in record.items():

        if isinstance(value, float) and math.isnan(value):
            clean_record[key] = None

        else:
            clean_record[key] = value

    return clean_record