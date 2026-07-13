"""
column_mapper.py

Central configuration for the Nifty100 Financial Intelligence Platform ETL.

Defines:
- Excel filename
- Target SQLite table
- Header row
- Sheet name
- Primary key
- Foreign key
- Required columns
- Column mappings
"""

WORKBOOK_CONFIG = {

    "companies.xlsx": {
        "table": "companies",
        "sheet": 0,
        "header": 1,
        "primary_key": "id",
        "foreign_key": None,
        "required_columns": [
            "id",
            "company_logo",
            "company_name",
            "chart_link",
            "about_company",
            "website",
            "nse_profile",
            "bse_profile",
            "face_value",
            "book_value",
            "roce_percentage",
            "roe_percentage"
        ],
        "column_mapping": {
            "id": "id",
            "company_logo": "company_logo",
            "company_name": "company_name",
            "chart_link": "chart_link",
            "about_company": "about_company",
            "website": "website",
            "nse_profile": "nse_profile",
            "bse_profile": "bse_profile",
            "face_value": "face_value",
            "book_value": "book_value",
            "roce_percentage": "roce_percentage",
            "roe_percentage": "roe_percentage"
        }
    },

    "analysis.xlsx": {
        "table": "analysis",
        "sheet": 0,
        "header": 1,
        "primary_key": "id",
        "foreign_key": "company_id",
        "required_columns": [
            "id",
            "company_id",
            "compounded_sales_growth",
            "compounded_profit_growth",
            "stock_price_cagr",
            "roe"
        ],
        "column_mapping": {
            "id": "id",
            "company_id": "company_id",
            "compounded_sales_growth": "compounded_sales_growth",
            "compounded_profit_growth": "compounded_profit_growth",
            "stock_price_cagr": "stock_price_cagr",
            "roe": "roe"
        }
    },

    "balancesheet.xlsx": {
        "table": "balancesheet",
        "sheet": 0,
        "header": 1,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "cashflow.xlsx": {
        "table": "cashflow",
        "sheet": 0,
        "header": 1,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "profitandloss.xlsx": {
        "table": "profitandloss",
        "sheet": 0,
        "header": 1,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "financial_ratios.xlsx": {
        "table": "financial_ratios",
        "sheet": 0,
        "header": 0,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "market_cap.xlsx": {
        "table": "market_cap",
        "sheet": 0,
        "header": 0,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "peer_groups.xlsx": {
        "table": "peer_groups",
        "sheet": 0,
        "header": 0,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "prosandcons.xlsx": {
        "table": "prosandcons",
        "sheet": 0,
        "header": 1,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "sectors.xlsx": {
        "table": "sectors",
        "sheet": 0,
        "header": 0,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "stock_prices.xlsx": {
        "table": "stock_prices",
        "sheet": 0,
        "header": 0,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    },

    "documents.xlsx": {
        "table": "documents",
        "sheet": 0,
        "header": 1,
        "primary_key": None,
        "foreign_key": "company_id",
        "required_columns": [],
        "column_mapping": {}
    }
}