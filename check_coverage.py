import sqlite3

conn = sqlite3.connect("database/nifty100.db")

columns = [
    row[1]
    for row in conn.execute(
        "PRAGMA table_info(financial_ratios)"
    ).fetchall()
    if row[1] not in ("id", "company_id", "year")
]

print("KPI COVERAGE")
print("=" * 60)

for column in columns:
    count = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM financial_ratios
        WHERE [{column}] IS NOT NULL
        """
    ).fetchone()[0]

    print(f"{column}: {count}")

print("\nTOTAL ROWS:")
print(
    conn.execute(
        "SELECT COUNT(*) FROM financial_ratios"
    ).fetchone()[0]
)

conn.close()