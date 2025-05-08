# agents/scheduler_agent/agent.py

import json
import dateparser
from datetime import timedelta
import requests
from agents.scheduler_agent.db import insert_event
from datetime import datetime, timedelta
from agents.scheduler_agent.reminders import schedule_reminder

OLLAMA_MODEL = "llama3.2"

def extract_event_ollama(user_input: str):
    prompt = f"""
Extract an event from the following sentence. Return ONLY a valid JSON object.

Sentence:
\"\"\"{user_input}\"\"\"

Return format:
{{
  "title": "...",
  "start_time": "...", 
  "end_time": "...",     
  "location": "..."       
}}

Rules:
- "end_time" and "location" can be null or omitted if not mentioned.
- DO NOT include anything outside the JSON.

Output:
"""

    try:
        res = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": OLLAMA_MODEL,  # ✅ use variable
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
        )

        if res.status_code != 200:
            return {"error": f"Ollama returned HTTP {res.status_code}"}

        data = res.json()
        raw = data.get("message", {}).get("content", "")

        if not raw:
            return {"error": "LLM returned empty response"}

        raw = raw.strip().strip("```json").strip("```").strip()

        return json.loads(raw)

    except Exception as e:
        return {"error": f"Failed to parse LLM output: {e}"}


def handle_schedule_input(user_input: str):
    result = extract_event_ollama(user_input)

    if "error" in result:
        return f"❌ LLM error: {result['error']}"

    try:
        title = result["title"]
        raw_start = result["start_time"]
        raw_end = result.get("end_time")
        location = result.get("location", "")

        start_dt = dateparser.parse(raw_start)
        end_dt = dateparser.parse(raw_end) if raw_end else None

        if not start_dt:
            return "❌ I couldn't understand the start time."

        # === 🛑 Prevent scheduling past events ===
        if start_dt < datetime.now():
            # 👇 OPTIONAL: trigger the reminder logic manually if it's just a test
            print(f"⚠️ Event '{title}' is in the past — running reminder now for testing.")
            print(f"🔔 Reminder: {title} in 10 minutes!")
            return f"⚠️ Event time has already passed — ran reminder manually: '{title}'"

        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat() if end_dt else None

        eid = insert_event(title, start_iso, end_iso, location, raw_text=user_input)
        reminder_time = start_dt - timedelta(minutes=10)
        schedule_reminder(eid, reminder_time, title)

        return f"✅ Got it. Scheduled '{title}' at {start_iso}."

    except Exception as e:
        return f"❌ Failed to schedule event: {str(e)}"
