from flask import Flask
import threading
import atexit
import secrets

from routes import events_page, event_page, user_page, jwt, bcrypt
from modules import reminders_manager, close_reminders_manager, limiter, socketioServer
from database import db

def create_app(config_name='default'):
    app = Flask(__name__)

    if config_name == 'test_config':
       app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_events.db' 

    else: 
       app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db' 

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
    db.init_app(app)

    app.register_blueprint(events_page)
    app.register_blueprint(event_page)
    app.register_blueprint(user_page)

    limiter.init_app(app)
    socketioServer.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)  
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    thread = threading.Thread(target=reminders_manager, args=[app.app_context()])
    thread.start()
    # When flask exists close reminders manager thread
    atexit.register(close_reminders_manager, thread)
    socketioServer.run(app, debug=True)
