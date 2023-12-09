from datetime import datetime, timedelta
from models import Event
import time
from database import db
import threading

exit_event = threading.Event()

def close_reminders_manager(thread: threading.Thread):
    exit_event.set()
    thread.join()

def reminders_manager(app_context):
    app_context.push()
    while True:
        if exit_event.is_set():
            return
        current_time = datetime.now()
        reminder_time = current_time + timedelta(minutes=30)

        events_to_remind = Event.query.filter(
            Event.hasReminder == False,
            Event.startDate >= current_time,
            Event.startDate <= reminder_time).all()

        # Send reminders for each event
        for event in events_to_remind:
            send_reminder(event.id, event.title)
            event = Event.query.get_or_404(event.id)
            event.hasReminder = True
            db.session.commit()

        time.sleep(60)

def send_reminder(event_id, title):
    print(f"Reminder for event '{title}' with ID {event_id}: The event is starting in 30 minutes!")
