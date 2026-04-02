import os
from dotenv import load_dotenv
from groq import Groq
import re
from datetime import datetime
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def convert_to_24hr(time_str):
    """Convert flexible time to HH:MM format"""
    try:
        time_str = time_str.replace(" ", "").lower()

        try:
            dt = datetime.strptime(time_str, "%I:%M%p")
        except:
            try:
                dt = datetime.strptime(time_str, "%I%p")
            except:
                try:
                    dt = datetime.strptime(time_str, "%H:%M")
                except:
                    return None

        return dt.strftime("%H:%M")
    except:
        return None


def parse_message(msg):
    msg_original = msg
    msg = msg.lower()

    # ---------- TRY GROQ ----------
    try:
        response = client.chat.completions.create(
            model="mixtral-70b-32768",
            messages=[{
                "role": "user",
                "content": f"""
                Extract task and time from this message:
                "{msg_original}"

                Return ONLY JSON:
                {{ "task": "...", "time": "HH:MM or 12hr format" }}
                """
            }]
        )

        output = response.choices[0].message.content.strip()

        match = re.search(r'\{.*\}', output)
        if match:
            data = json.loads(match.group())

            task = data.get("task") or "Reminder"
            raw_time = data.get("time")

            time_val = convert_to_24hr(raw_time) if raw_time else None

            if task and time_val:
                return task, time_val

    except Exception as e:
        print("Groq AI Error:", e)

    # ---------- FALLBACK PARSER ----------
    time_match = re.search(
        r'(\d{1,2}:\d{2}\s*(am|pm)?|\d{1,2}\s*(am|pm))',
        msg
    )

    if time_match:
        raw_time = time_match.group()
        time_val = convert_to_24hr(raw_time)
    else:
        time_val = None

    # Extract task
    task = re.sub(r'remind me (to )?', '', msg)
    if time_match:
        task = task.replace(time_match.group(), '')

    task = task.strip()

    if task.endswith(' at'):
        task = task[:-3].strip()

    if not task:
        task = "Reminder"

    return task, time_val