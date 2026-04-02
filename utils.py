import os
from dotenv import load_dotenv
from groq import Groq
import re
from datetime import datetime
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_message(msg):
    msg_original = msg
    msg = msg.lower()

    # --- Try Groq AI ---
    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # ✅ updated model
            messages=[{
                "role": "user",
                "content": f"""
                Extract task and time from this message:
                "{msg_original}"

                Return ONLY JSON:
                {{ "task": "...", "time": "HH:MM" }}
                """
            }]
        )

        output = response.choices[0].message.content.strip()

        match = re.search(r'\{.*\}', output)
        if match:
            data = json.loads(match.group())
            task = data.get("task") or "Reminder"
            time_val = data.get("time")

            if task and time_val:
                return task, time_val

    except Exception as e:
        print("Groq AI Error:", e)

    # --- Fallback parser ---
    time_match = re.search(r'(\d{1,2}[: ]\d{2}\s*(am|pm)?|\d{1,2}\s*(am|pm))', msg)

    if time_match:
        time_str = time_match.group().replace(" ", "")
        try:
            dt = datetime.strptime(time_str, "%I:%M%p")
        except:
            try:
                dt = datetime.strptime(time_str, "%I%p")
            except:
                try:
                    dt = datetime.strptime(time_str, "%H:%M")
                except:
                    dt = None

        time_val = dt.strftime("%H:%M") if dt else None
    else:
        time_val = None

    # Extract task
    task = re.sub(r'remind me (to )?', '', msg)
    if time_match:
        task = task.replace(time_match.group(), '')
    task = task.strip()

    if task.lower().endswith(' at'):
        task = task[:-3].strip()

    if not task:
        task = "Reminder"

    return task, time_val