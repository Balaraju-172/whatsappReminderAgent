from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from db import add_reminder
from utils import parse_message
import threading
from scheduler import run_scheduler
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Start scheduler
threading.Thread(target=run_scheduler, daemon=True).start()

@app.route("/webhook", methods=['POST'])
def webhook():
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')

    # Ensure correct format
    if not sender.startswith("whatsapp:"):
        sender = "whatsapp:" + sender.lstrip("+")

    task, time_val = parse_message(incoming_msg)

    resp = MessagingResponse()

    if task and time_val:
        add_reminder(sender, task, time_val)
        resp.message(f"✅ Reminder set at {time_val} for: {task}")
    else:
        resp.message("❌ Could not understand. Try: Remind me to study at 6pm")

    return str(resp)

@app.route("/")
def home():
    return "Bot running 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)