import sqlite3, os

DB_PATH = "server_data/events.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            start_ts TEXT,
            end_ts TEXT,
            location TEXT,
            raw_text TEXT
        )
        """)
init_db()

def insert_event(title, start_ts, end_ts=None, location=None, raw_text=""):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO events (title, start_ts, end_ts, location, raw_text)
            VALUES (?, ?, ?, ?, ?)
        """, (title, start_ts, end_ts, location, raw_text))
        return c.lastrowid

def get_events_on_day(date_str):
    """Return all events on a given date (YYYY-MM-DD)"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM events
            WHERE DATE(start_ts) = ?
            ORDER BY start_ts
        """, (date_str,))
        return c.fetchall()
