"""
SQLite database connection.
"""

from pathlib import Path
import sqlite3

DB_PATH = Path("db/nifty100.db")


def get_connection():
    """
    Create SQLite connection with foreign keys enabled.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.execute("PRAGMA foreign_keys = ON;")

    return conn