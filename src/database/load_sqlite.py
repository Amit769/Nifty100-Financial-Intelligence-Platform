"""
Verify SQLite database.
"""

from .connection import get_connection


def show_tables():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
    """)

    tables = cursor.fetchall()

    print("\nTables in database:\n")

    for table in tables:
        print(f"• {table[0]}")

    conn.close()


if __name__ == "__main__":
    show_tables()