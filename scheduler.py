import os
import time
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from db import get_reminders, delete_reminder

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

print("SID:", TWILIO_ACCOUNT_SID)
print("TOKEN:", TWILIO_AUTH_TOKEN)
print("FROM:", TWILIO_WHATSAPP_NUMBER)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def run_scheduler():
    print("Scheduler started ✅")
    while True:
        check_reminders()
        time.sleep(30)

def check_reminders():
    now = datetime.now().strftime("%H:%M")
    print(f"[Scheduler] Checking at {now}")

    reminders = get_reminders()

    for reminder in reminders:
        reminder_id, user, task, time_val = reminder

        print(f"Found reminder → {user} | {task} | {time_val}")

        if time_val == now:
            try:
                print(f"Sending reminder to {user}: {task}")

                client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=user,
                    body=f"⏰ Reminder: {task}"
                )

                delete_reminder(reminder_id)

            except Exception as e:
                print("❌ Twilio Error:", e)