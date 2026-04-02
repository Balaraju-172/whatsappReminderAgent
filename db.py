import sqlite3

conn = sqlite3.connect("reminders.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    task TEXT,
    time TEXT
)
""")
conn.commit()

def add_reminder(user, task, time):
    cursor.execute(
        "INSERT INTO reminders (user, task, time) VALUES (?, ?, ?)",
        (user, task, time)
    )
    conn.commit()

def get_reminders():
    cursor.execute("SELECT * FROM reminders")
    return cursor.fetchall()

def delete_reminder(reminder_id):
    cursor.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    conn.commit()