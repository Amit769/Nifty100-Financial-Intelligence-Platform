"""
Ranking Engine
==============

Converts financial metrics into comparable 0–100 scores
and produces a weighted quality ranking.
"""
from src.screener.engine import run_screener
import pandas as pd


def rank_screened_companies(
    filters=None,
):
    """
    Run the screener and rank the resulting companies.
    """

    screened_data = run_screener(
        filters=filters,
    )

    ranked_rows = []

    for _, row in screened_data.iterrows():

        scores = calculate_ranking_scores(
            row
        )

        ranked_rows.append(
            {
                "company_id": row["company_id"],
                "company_name": row["company_name"],
                "broad_sector": row["broad_sector"],
                **scores,
            }
        )

    ranked_data = pd.DataFrame(
        ranked_rows
    )

    if ranked_data.empty:
        return ranked_data

    return ranked_data.sort_values(
        "ranking_score",
        ascending=False,
    ).reset_index(drop=True)


def normalize_higher_is_better(
    value,
    minimum,
    maximum,
):
    """
    Normalize a metric where higher values are better.

    Returns a score between 0 and 100.
    """

    if value is None:
        return None

    if maximum == minimum:
        return 50.0

    score = (
        (value - minimum)
        / (maximum - minimum)
    ) * 100

    return max(
        0.0,
        min(100.0, score),
    )


def normalize_lower_is_better(
    value,
    minimum,
    maximum,
):
    """
    Normalize a metric where lower values are better.

    Returns a score between 0 and 100.
    """

    if value is None:
        return None

    if maximum == minimum:
        return 50.0

    score = (
        (maximum - value)
        / (maximum - minimum)
    ) * 100

    return max(
        0.0,
        min(100.0, score),
    )
    
RANKING_WEIGHTS = {
    "profitability": 0.25,
    "growth": 0.20,
    "financial_strength": 0.20,
    "cash_flow": 0.15,
    "valuation": 0.10,
    "dividend": 0.10,
}
    
METRIC_RANGES = {
    "return_on_equity_pct": (0, 30),
    "return_on_capital_employed_pct": (0, 30),
    "net_profit_margin_pct": (0, 30),

    "revenue_cagr_5yr": (-10, 30),
    "pat_cagr_5yr": (-10, 30),
    "eps_cagr_5yr": (-10, 30),

    "debt_to_equity": (0, 5),
    "interest_coverage": (0, 50),

    "cfo_quality_score": (0, 1),
    "fcf_conversion_rate_pct": (-100, 200),

    "pe_ratio": (0, 100),
    "pb_ratio": (0, 20),

    "dividend_yield_pct": (0, 10),
}
    
    
def calculate_category_score(
    row,
    metrics,
    lower_is_better=None,
):
    """
    Calculate the average score for a group of metrics.
    """

    if lower_is_better is None:
        lower_is_better = set()

    scores = []

    for metric in metrics:

        value = row.get(metric)

        if value is None:
            continue

        minimum, maximum = METRIC_RANGES[metric]

        if metric in lower_is_better:
            score = normalize_lower_is_better(
                value,
                minimum,
                maximum,
            )
        else:
            score = normalize_higher_is_better(
                value,
                minimum,
                maximum,
            )

        if score is not None:
            scores.append(score)

    if not scores:
        return None

    return sum(scores) / len(scores)

CATEGORY_METRICS = {
    "profitability": [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
    ],

    "growth": [
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ],

    "financial_strength": [
        "debt_to_equity",
        "interest_coverage",
    ],

    "cash_flow": [
        "cfo_quality_score",
        "fcf_conversion_rate_pct",
    ],

    "valuation": [
        "pe_ratio",
        "pb_ratio",
    ],

    "dividend": [
        "dividend_yield_pct",
    ],
}

LOWER_IS_BETTER = {
    "debt_to_equity",
    "pe_ratio",
    "pb_ratio",
}

def calculate_ranking_scores(row):
    """
    Calculate category scores and final weighted ranking score
    for a single company.
    """

    category_scores = {}

    for category, metrics in CATEGORY_METRICS.items():

        category_scores[category] = calculate_category_score(
            row,
            metrics,
            lower_is_better=LOWER_IS_BETTER,
        )

    weighted_components = []

    for category, weight in RANKING_WEIGHTS.items():

        score = category_scores.get(category)

        if score is not None:
            weighted_components.append(
                score * weight
            )

    if not weighted_components:
        final_score = None
    else:
        final_score = sum(
            weighted_components
        )

    return {
        **category_scores,
        "ranking_score": final_score,
    }
    
def calculate_ranking_score(row):
    """
    Calculate a weighted 0-100 ranking score for one company.

    Parameters
    ----------
    row : dict-like
        One company's financial metrics.

    Returns
    -------
    float or None
        Final weighted ranking score between 0 and 100.
    """

    category_scores = {}

    # -------------------------
    # Profitability
    # -------------------------
    profitability_metrics = [
        ("return_on_equity_pct", "higher"),
        ("return_on_capital_employed_pct", "higher"),
        ("net_profit_margin_pct", "higher"),
    ]

    # -------------------------
    # Growth
    # -------------------------
    growth_metrics = [
        ("revenue_cagr_5yr", "higher"),
        ("pat_cagr_5yr", "higher"),
        ("eps_cagr_5yr", "higher"),
    ]

    # -------------------------
    # Financial Strength
    # -------------------------
    financial_strength_metrics = [
        ("debt_to_equity", "lower"),
        ("interest_coverage", "higher"),
    ]

    # -------------------------
    # Cash Flow
    # -------------------------
    cash_flow_metrics = [
        ("cfo_quality_score", "higher"),
        ("fcf_conversion_rate_pct", "higher"),
    ]

    # -------------------------
    # Valuation
    # -------------------------
    valuation_metrics = [
        ("pe_ratio", "lower"),
        ("pb_ratio", "lower"),
    ]

    # -------------------------
    # Dividend
    # -------------------------
    dividend_metrics = [
        ("dividend_yield_pct", "higher"),
    ]

    metric_groups = {
        "profitability": profitability_metrics,
        "growth": growth_metrics,
        "financial_strength": financial_strength_metrics,
        "cash_flow": cash_flow_metrics,
        "valuation": valuation_metrics,
        "dividend": dividend_metrics,
    }

    # Calculate average score for each category
    for category, metrics in metric_groups.items():

        scores = []

        for metric, direction in metrics:

            value = row.get(metric)

            if value is None:
                continue

            if metric not in METRIC_RANGES:
                continue

            minimum, maximum = METRIC_RANGES[metric]

            if direction == "higher":
                score = normalize_higher_is_better(
                    value,
                    minimum,
                    maximum,
                )

            else:
                score = normalize_lower_is_better(
                    value,
                    minimum,
                    maximum,
                )

            if score is not None:
                scores.append(score)

        if scores:
            category_scores[category] = sum(scores) / len(scores)

    # No usable metrics
    if not category_scores:
        return None

    # Weighted final score
    weighted_score = 0.0
    total_weight = 0.0

    for category, score in category_scores.items():

        weight = RANKING_WEIGHTS.get(
            category,
            0,
        )

        weighted_score += score * weight
        total_weight += weight

    if total_weight == 0:
        return None

    return weighted_score / total_weight    

def rank_companies(data):
    """
    Calculate ranking scores for all companies
    and return them sorted from highest to lowest.
    """

    result = data.copy()

    # Calculate one score for every company
    result["ranking_score"] = result.apply(
        calculate_ranking_score,
        axis=1,
    )

    # Sort highest score first
    result = result.sort_values(
        "ranking_score",
        ascending=False,
    )

    return result.reset_index(drop=True)