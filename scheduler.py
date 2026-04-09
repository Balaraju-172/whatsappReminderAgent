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
        time.sleep(60)  # check every 1 minute

def check_reminders():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("\n-----------------------------")
    print(f"⏱️ Current Time: {current_time}")

    reminders = get_reminders()

    if not reminders:
        print("📭 No reminders found")
        return

    for reminder in reminders:
        reminder_id, user, task, time_val = reminder

        print(f"\n📌 Reminder ID: {reminder_id}")
        print(f"👤 User: {user}")
        print(f"📝 Task: {task}")
        print(f"🕒 Stored Time: {time_val}")

        if time_val:
            try:
                # Convert stored time to today's datetime
                reminder_time = datetime.strptime(time_val, "%H:%M")
                reminder_time = reminder_time.replace(
                    year=now.year,
                    month=now.month,
                    day=now.day
                )

                print(f"⏰ Reminder Time (today): {reminder_time.strftime('%H:%M:%S')}")

                # Calculate time difference
                time_diff = (now - reminder_time).total_seconds()
                print(f"⌛ Time Difference: {time_diff:.2f} seconds")

                # Trigger if within 0–60 seconds
                if 0 <= time_diff < 60:
                    print(f"🔥 TRIGGERED → Sending reminder to {user}")

                    client.messages.create(
                        from_=TWILIO_WHATSAPP_NUMBER,
                        to=user,
                        body=f"⏰ Reminder: {task}"
                    )

                    delete_reminder(reminder_id)
                    print("✅ Reminder sent & deleted")
                elif time_diff < 0:
                    print("⏳ Not yet time")
                else:
                    print("⚠️ Missed window (more than 60s late)")

            except Exception as e:
                print(f"❌ Error for reminder {reminder_id}: {e}")