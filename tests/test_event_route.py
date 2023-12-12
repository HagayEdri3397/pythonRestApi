from datetime import datetime
import pytest
from app import create_app, db
from models import Event, User
from flask_bcrypt import Bcrypt

app = create_app('test_config')
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

def test_create_event(client):
    data = {
        "title": "new party",
        "location": "Tel aviv",
        "venue": "Habima",
        "startDate": "2023-12-10 21:23:00",
        "participants": "300"
    }

    response = client.post('/api/event', json=data)

    assert response.status_code == 201
    assert response.json['message'] == "Event scheduled successfully"


def test_get_event(client):
    insert_mock_data()

    response = client.get('/api/event/1')
    assert response.status_code == 200
    assert 'event' in response.json

def test_get_nonexistent_event(client):
    response = client.get('/api/event/9999')

    assert response.status_code == 404
    assert response.json['error'] == "Event not found"

def test_delete_event(client):
    insert_mock_data()
        
    response = client.delete('/api/event/1')
    assert response.status_code == 200
    assert response.json['message'] == "Event deleted successfully"

def test_update_event(client):
    insert_mock_data()

    update_data = {
        "title": "new party",
        "location": "Tel aviv",
        "venue": "Habima",
        "startDate": "2023-12-10 21:30:00",
        "participants": "400"
    }

    response = client.put('/api/event/1', json=update_data)

    assert response.status_code == 200
    assert response.json['message'] == "Event updated successfully"

def insert_mock_data():
    with app.app_context():
        data = {
            "title": "new party",
            "location": "Tel Aviv",
            "venue": "Habima",
            "startDate": datetime.strptime("2023-12-10 21:23:00", '%Y-%m-%d %H:%M:%S'),
            "participants": "300"
        }
        event_instance = Event(**data)
        db.session.add(event_instance)
        db.session.commit() 

def insert_mock_user_and_event(user, event, toSubscribe = False):
    with app.app_context():
        bcrypt = Bcrypt()
        user.password = bcrypt.generate_password_hash(user.password).decode('utf-8')
        if toSubscribe:
            event.subscribers.append(user)
        
        db.session.add(user)
        db.session.add(event)
        db.session.commit()

def register_new_user(client, username):
    # Helper function to get a JWT token for a user
    response = client.post('/api/register', json={'username': username, 'password': 'password'})
    return response.status_code == 201

def get_auth_token(client, username):
    # Helper function to get a JWT token for a user
    response = client.post('/api/login', json={'username': username, 'password': 'password'})
    return response.json['access_token']

def test_subscribe_event(client):
    user = User(username='test_user', password='password')
    event = Event(title='Test Event', location='Test Location', venue='Test Venue', startDate = datetime.strptime("2023-12-10 21:23:00", '%Y-%m-%d %H:%M:%S'), participants=100)
    insert_mock_user_and_event(user, event)

    # Get JWT token for the user
    token = get_auth_token(client, 'test_user')

    # Make a POST request to subscribe to the event
    response = client.post('/api/event/subscribe/1', headers={'Authorization': f'Bearer {token}'})

    print(f"Token: {token}")
    print(f"Response JSON: {response.json}")
    # Assert that the subscription is successful
    assert response.status_code == 200
    assert response.json['message'] == "Subscribed to the event"

def test_unsubscribe_event(client):
    user = User(username='test_user', password='password')
    event = Event(title='Test Event', location='Test Location', venue='Test Venue', startDate = datetime.strptime("2023-12-10 21:23:00", '%Y-%m-%d %H:%M:%S'), participants=100)
    insert_mock_user_and_event(user, event, True)

    # Get JWT token for the user
    token = get_auth_token(client, 'test_user')

    # Make a POST request to unsubscribe from the event
    response = client.post('/api/event/unsubscribe/1', headers={'Authorization': f'Bearer {token}'})

    # Assert that the unsubscription is successful
    assert response.status_code == 200
    assert response.json['message'] == "Unsubscribed to the event"