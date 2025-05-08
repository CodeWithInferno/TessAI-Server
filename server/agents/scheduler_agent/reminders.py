# agents/scheduler_agent/reminders.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import threading

# Initialize the scheduler in its own thread
_scheduler_lock = threading.Lock()
scheduler = BackgroundScheduler()
scheduler.start()

def schedule_reminder(event_id: int, remind_time: datetime, title: str):
    """
    Schedules a reminder 10 minutes before the event.
    """
    with _scheduler_lock:
        job_id = f"reminder_{event_id}"
        
        # Avoid duplicating the job
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        scheduler.add_job(
            func=lambda: print(f"🔔 Reminder: {title} in 10 minutes!"),
            trigger="date",
            run_date=remind_time,
            id=job_id,
            replace_existing=True
        )
        print(f"⏰ [Reminder Scheduled] {title} at {remind_time.isoformat()}")
