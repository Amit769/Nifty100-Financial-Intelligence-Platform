import sqlite3

conn = sqlite3.connect("database/nifty100.db")

rows = conn.execute(
    """
    SELECT
        s.company_id,
        c.company_name,
        COUNT(fr.id) AS ratio_rows,
        SUM(
            CASE
                WHEN fr.high_leverage_flag = 1
                THEN 1
                ELSE 0
            END
        ) AS high_leverage_warnings
    FROM sectors s
    JOIN companies c
        ON c.id = s.company_id
    LEFT JOIN financial_ratios fr
        ON fr.company_id = s.company_id
    WHERE s.broad_sector = 'Financials'
    GROUP BY s.company_id, c.company_name
    ORDER BY s.company_id
    """
).fetchall()

print("FINANCIALS SECTOR COMPANIES")
print("=" * 80)

for row in rows:
    print(row)

print("\nTOTAL FINANCIALS COMPANIES:", len(rows))

conn.close()