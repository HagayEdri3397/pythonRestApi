from flask_socketio import SocketIO
socketioServer = SocketIO()


@socketioServer.on('connect')
def handle_connect():
    print('Client connected')

@socketioServer.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# @socketio.on('event_update')
# def handle_event_update(data):
#     event_id = data.get('event_id')
#     message = data.get('message')

#     # Notify subscribers
#     notify_subscribers(event_id, message)

#     # Broadcast the update to all connected clients
#     socketio.emit('event_updated', {'event_id': event_id, 'message': message}, broadcast=True)

# def notify_subscribers(event_type, event_id, subscribers, message):
#     # Broadcast the update to all connected clients
#     socketio.emit(f'event_{event_type}', {'event_id': event_id, 'message': message}, broadcast=True)
# def notify_subscribers(event_id, message):
#     event = Event.query.get(event_id)
#     for user in event.subscribers:
#         print(f"Notification sent to {user.username}: {message}")

#         # Emit a WebSocket event to the specific user
#         socketio.emit('event_updated', {'event_id': event_id, 'message': message}, room=user.id)