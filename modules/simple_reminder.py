def notify_subscribers(event_id, subscribers, event_type):
    print(subscribers)
    for user in subscribers:
        message = f"The event {event_id} has {event_type}"
        print(f"Notification sent to {user.username}: {message}")