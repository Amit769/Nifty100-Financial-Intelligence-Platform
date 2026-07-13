-- ==========================================
-- Nifty100 Financial Intelligence Platform
-- Exploratory Queries
-- ==========================================

-- 1. Total companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- 2. List all companies
SELECT id, company_name
FROM companies
ORDER BY company_name;

-- 3. Companies by sector
SELECT sector, COUNT(*) AS companies
FROM sectors
GROUP BY sector
ORDER BY companies DESC;

-- 4. Top 10 companies by Market Cap
SELECT company_id, market_cap
FROM market_cap
ORDER BY market_cap DESC
LIMIT 10;

-- 5. Total stock price records
SELECT COUNT(*) AS total_records
FROM stock_prices;

-- 6. Stock records per company
SELECT company_id, COUNT(*) AS records
FROM stock_prices
GROUP BY company_id
ORDER BY records DESC;

-- 7. Average ROE
SELECT AVG(CAST(roe AS REAL)) AS avg_roe
FROM analysis;

-- 8. Companies having documents
SELECT company_id, COUNT(*) AS total_docs
FROM documents
GROUP BY company_id
ORDER BY total_docs DESC;

-- 9. Companies with maximum assets
SELECT company_id, MAX(total_assets)
FROM balancesheet
GROUP BY company_id
ORDER BY MAX(total_assets) DESC
LIMIT 10;

-- 10. Companies with highest sales CAGR
SELECT company_id, compounded_sales_growth
FROM analysis
ORDER BY compounded_sales_growth DESC;