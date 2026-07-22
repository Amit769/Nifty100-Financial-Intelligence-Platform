import pandas as pd

from src.ranking.engine import (
    calculate_ranking_score,
    rank_companies,
)


def test_score_is_between_zero_and_hundred():
    row = {
        "return_on_equity_pct": 20,
        "return_on_capital_employed_pct": 25,
        "net_profit_margin_pct": 15,
        "revenue_cagr_5yr": 12,
        "pat_cagr_5yr": 15,
        "eps_cagr_5yr": 10,
        "debt_to_equity": 0.5,
        "interest_coverage": 10,
        "cfo_quality_score": 0.8,
        "fcf_conversion_rate_pct": 80,
        "pe_ratio": 25,
        "pb_ratio": 5,
        "dividend_yield_pct": 2,
    }

    score = calculate_ranking_score(row)

    assert score is not None
    assert 0 <= score <= 100


def test_missing_values_do_not_crash():
    row = {
        "return_on_equity_pct": 20,
        "debt_to_equity": None,
        "pe_ratio": None,
    }

    score = calculate_ranking_score(row)

    assert score is not None
    assert 0 <= score <= 100


def test_higher_roe_improves_score():
    low_roe = {
        "return_on_equity_pct": 10,
    }

    high_roe = {
        "return_on_equity_pct": 25,
    }

    assert (
        calculate_ranking_score(high_roe)
        > calculate_ranking_score(low_roe)
    )


def test_lower_debt_to_equity_improves_score():
    low_debt = {
        "debt_to_equity": 0.5,
    }

    high_debt = {
        "debt_to_equity": 3.0,
    }

    assert (
        calculate_ranking_score(low_debt)
        > calculate_ranking_score(high_debt)
    )


def test_lower_pe_improves_valuation_score():
    low_pe = {
        "pe_ratio": 15,
    }

    high_pe = {
        "pe_ratio": 60,
    }

    assert (
        calculate_ranking_score(low_pe)
        > calculate_ranking_score(high_pe)
    )


def test_rank_companies_creates_sorted_ranking():

    data = pd.DataFrame(
        [
            {
                "company_id": "A",
                "company_name": "Company A",
                "return_on_equity_pct": 25,
            },
            {
                "company_id": "B",
                "company_name": "Company B",
                "return_on_equity_pct": 10,
            },
        ]
    )

    result = rank_companies(data)

    assert "ranking_score" in result.columns

    assert (
        result.iloc[0]["company_id"]
        == "A"
    )

    assert (
        result.iloc[0]["ranking_score"]
        >= result.iloc[1]["ranking_score"]
    )