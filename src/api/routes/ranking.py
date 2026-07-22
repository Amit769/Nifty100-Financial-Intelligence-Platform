from fastapi import APIRouter, HTTPException

from src.screener.engine import load_latest_financial_data
from src.ranking.engine import rank_companies


router = APIRouter(
    prefix="/ranking",
    tags=["Ranking"],
)


@router.get("/")
def get_ranking():
    """
    Return all companies ranked by financial quality score.
    """

    data = load_latest_financial_data()

    ranked = rank_companies(data)

    records = ranked[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "sub_sector",
            "ranking_score",
        ]
    ].to_dict(
        orient="records"
    )

    return records


@router.get("/{company_id}")
def get_company_ranking(company_id: str):
    """
    Return ranking information for one company.
    """

    data = load_latest_financial_data()

    ranked = rank_companies(data)

    company = ranked[
        ranked["company_id"].str.upper()
        == company_id.upper()
    ]

    if company.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_id}' not found",
        )

    result = company[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "sub_sector",
            "ranking_score",
        ]
    ]

    return result.to_dict(
        orient="records"
    )[0]