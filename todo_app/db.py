import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_NAME = BASE_DIR / "tasks.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row

    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    return conn
