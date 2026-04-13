# db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_conn = None


def _get_conn():
    """Return a cached database connection, creating it on first call.

    Deferring the connection to first use ensures that DATABASE_URL is
    fully resolved by the time we try to connect, avoiding the
    OperationalError that occurs when psycopg2 is called at import time
    before the environment variable is available.
    """
    global _conn
    if _conn is None or _conn.closed:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set")
        _conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        # Create table if not exists (runs once per connection)
        with _conn.cursor() as cur:
            cur.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    "user" TEXT,
    task TEXT,
    "time" TEXT
)
""")
        _conn.commit()
    return _conn


def add_reminder(user, task, time_val):
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO reminders (\"user\", task, \"time\") VALUES (%s, %s, %s)",
            (user, task, time_val)
        )
    conn.commit()


def get_reminders():
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM reminders")
        return cur.fetchall()


def delete_reminder(reminder_id):
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM reminders WHERE id=%s", (reminder_id,))
    conn.commit()