# db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user TEXT,
    task TEXT,
    time TEXT
)
""")
conn.commit()

def add_reminder(user, task, time_val):
    cursor.execute(
        "INSERT INTO reminders (user, task, time) VALUES (%s, %s, %s)",
        (user, task, time_val)
    )
    conn.commit()

def get_reminders():
    cursor.execute("SELECT * FROM reminders")
    return cursor.fetchall()

def delete_reminder(reminder_id):
    cursor.execute("DELETE FROM reminders WHERE id=%s", (reminder_id,))
    conn.commit()