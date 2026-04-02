import os
import time
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from db import get_reminders, delete_reminder

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def run_scheduler():
    print("Scheduler started ✅")
    while True:
        check_reminders()
        time.sleep(10)  # check every 10 seconds


def check_reminders():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    print(f"[Scheduler] Checking at {current_time}")

    reminders = get_reminders()

    for reminder in reminders:
        reminder_id, user, task, time_val = reminder

        print(f"Found reminder → {user} | {task} | {time_val}")

        if time_val:
            try:
                # ✅ Convert stored time to today's datetime
                reminder_time = datetime.strptime(time_val, "%H:%M")
                reminder_time = reminder_time.replace(
                    year=now.year,
                    month=now.month,
                    day=now.day
                )

                # 🔥 CRITICAL FIX: precise time window
                time_diff = (now - reminder_time).total_seconds()

                # ✅ Only send within 0–60 seconds AFTER exact time
                # (prevents early trigger + allows small delay)
                if 0 <= time_diff < 60:
                    print(f"🔥 Sending reminder to {user}: {task}")

                    client.messages.create(
                        from_=TWILIO_WHATSAPP_NUMBER,
                        to=user,
                        body=f"⏰ Reminder: {task}"
                    )

                    # ✅ Delete after sending
                    delete_reminder(reminder_id)

            except Exception as e:
                print(f"❌ Error sending reminder {reminder_id}:", e)