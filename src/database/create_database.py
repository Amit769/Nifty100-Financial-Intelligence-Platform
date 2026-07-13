"""
Create SQLite database from schema.sql.
"""

from pathlib import Path

from .connection import get_connection


SCHEMA_PATH = Path("db/schema.sql")


def create_database():

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"{SCHEMA_PATH} not found.")

    conn = get_connection()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()

    conn.close()

    print("Database created successfully.")


if __name__ == "__main__":
    create_database()