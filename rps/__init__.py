from .config import SQLITE_DB
import sqlite3


conn = sqlite3.connect(SQLITE_DB)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS run_record (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    length REAL,
    turn_num INTEGER,
    detail_length TEXT,
    time TEXT
)"""
)
conn.commit()
