from flask import Flask
import threading
import atexit
import secrets

from routes import events_page, event_page, user_page, jwt, bcrypt
from modules import reminders_manager, close_reminders_manager, limiter
from database import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
db.init_app(app)

app.register_blueprint(events_page)
app.register_blueprint(event_page)
app.register_blueprint(user_page)
limiter.init_app(app)
# socketioServer.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)

# from flask_socketio import SocketIO
# socketio = SocketIO(app)


# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
def handle_offchain(app_context):
# this will give access to context
    app_context.push()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    thread = threading.Thread(target=reminders_manager, args=[app.app_context()])
    thread.start()
    # When flask exists close reminders manager thread
    atexit.register(close_reminders_manager, thread)
    app.run(debug=True)
