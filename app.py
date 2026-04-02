from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from db import add_reminder
from utils import parse_message
from scheduler import run_scheduler
from dotenv import load_dotenv
import os
import threading

# Load environment variables from .env
load_dotenv()

# Create Flask app
app = Flask(__name__)

# ---------------------------------------------------
# ✅ FIX: Start scheduler AFTER first request
# This ensures it works on Render (important)
# ---------------------------------------------------
@app.before_first_request
def start_scheduler():
    print("🚀 Starting scheduler thread...")
    threading.Thread(target=run_scheduler, daemon=True).start()


# ---------------------------------------------------
# 📩 Webhook route (Twilio sends messages here)
# ---------------------------------------------------
@app.route("/webhook", methods=['POST'])
def webhook():
    # Get message and sender from Twilio request
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')

    # Ensure sender format is correct (whatsapp:+91xxxx)
    if not sender.startswith("whatsapp:"):
        sender = "whatsapp:" + sender.lstrip("+")

    # Parse message → extract task + time
    task, time_val = parse_message(incoming_msg)

    # Prepare Twilio response
    resp = MessagingResponse()

    # If parsing successful → save reminder
    if task and time_val:
        add_reminder(sender, task, time_val)

        resp.message(f"✅ Reminder set at {time_val} for: {task}")
    else:
        resp.message("❌ Could not understand. Try: Remind me to study at 6pm")

    return str(resp)


# ---------------------------------------------------
# 🏠 Home route (used by Render / UptimeRobot)
# ---------------------------------------------------
@app.route("/")
def home():
    return "Bot running 🚀"


# ---------------------------------------------------
# 🚀 Run app (Render-compatible)
# ---------------------------------------------------
if __name__ == "__main__":
    # Render provides PORT environment variable
    port = int(os.environ.get("PORT", 10000))

    # Run Flask app on all IPs (required for deployment)
    app.run(host="0.0.0.0", port=port)