# agents/scheduler_agent/schema.py

schedule_event_schema = {
    "name": "schedule_event",
    "description": "Schedule a new personal event",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "What the event is (e.g. Lunch with Sam)"
            },
            "start_time": {
                "type": "string",
                "description": "When the event starts (natural language like 'tomorrow at 2pm')"
            },
            "end_time": {
                "type": "string",
                "description": "When the event ends (optional)"
            },
            "location": {
                "type": "string",
                "description": "Where the event takes place (optional)"
            }
        },
        "required": ["title", "start_time"]
    }
}
