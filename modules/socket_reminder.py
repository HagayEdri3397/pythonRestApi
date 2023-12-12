from flask_socketio import SocketIO
socketioServer = SocketIO(cors_allowed_origins="*")

@socketioServer.on('connect')
def handle_connect():
    print(f'Client connected')

@socketioServer.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

from flask_socketio import join_room, leave_room

# Client can join to room and get real-time updates about event status 
@socketioServer.on('join')
def on_join(data):
    if not data['room']: 
        return
    event_id = data['room']
    room = f'event_{event_id}'
    print(f'user joined to room {room}')
    join_room(room)

@socketioServer.on('leave')
def on_leave(data):
    if not data['room']: 
        return
    event_id = data['room']
    room = f'event_{event_id}'
    print(f'user joined to room {room}')
    leave_room(room)

def notify_subscribers_ws(event_id, event_type):
    message = f"The event {event_id} has {event_type}"
    data = {'event_id': event_id, 'data': message}
    room = f'event_{event_id}'
    socketioServer.emit(f'event_{event_type}', data,to = room)