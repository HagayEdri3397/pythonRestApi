from flask import Flask
import threading
import atexit

from routes import events_page, event_page
from modules import reminders_manager, close_reminders_manager, limiter
from database import db

app = Flask(__name__)

limiter.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db.init_app(app)

app.register_blueprint(events_page)
app.register_blueprint(event_page)

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
