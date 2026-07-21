import sqlite3

conn = sqlite3.connect("database/nifty100.db")

rows = conn.execute(
    """
    SELECT broad_sector, COUNT(*)
    FROM sectors
    GROUP BY broad_sector
    """
).fetchall()

for row in rows:
    print(row)

conn.close()