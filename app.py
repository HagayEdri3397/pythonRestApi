from flask import Flask, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select, create_engine
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import sched
import time
import threading
from const_params.const import HTTP_BAD_REQUEST, HTTP_CREATED,HTTP_NOT_FOUND, HTTP_INTERNAL_SERVER_ERROR
from validation.validationService import validate_event_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)
engine = create_engine("sqlite:///events.db") 

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    venue = db.Column(db.String(100))
    participants = db.Column(db.Integer)
    startDate = db.Column(db.DateTime, nullable=False)
    createDate = db.Column(db.DateTime, default=func.now())
    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'venue': self.venue,
            'participants': self.participants, 
            'startDate': self.startDate.strftime('%Y-%m-%d %H:%M:%S'),
            'createDate': self.createDate.strftime('%Y-%m-%d %H:%M:%S')
        }


def remindManager():
    while True:
        current_time = datetime.now()
        
        # res = getEventsToRemined()
        # print(res)
        # for event in events_reminders_list:
        #     print(event.startDate)
        #     if event.startDate - timedelta(minutes=30) <= current_time:
        #         send_reminder(event.id, event.title)
        #         events_reminders_list.remove(event)
        time.sleep(1)

def getEventsToRemined():
    current_time = datetime.now()
    stmt = select(Event).where(Event.startDate -timedelta(minutes=30) <= current_time)
    with engine.connect() as conn:
        results = conn.execute(stmt).scalars()
    return results

def send_reminder(event_id, title):
    print(f"Reminder for event '{title}' with ID {event_id}: The event is starting in 30 minutes!")
    
@app.route('/api/event', methods=['POST'])
def schedule_event():
    try:
        request_data = request.get_json(force=True)
        validate_event_data(request_data)
        new_event = Event(title=request_data['title'],
                      location=request_data.get('location'),
                      venue=request_data.get('venue'),
                      startDate=datetime.strptime(request_data['startDate'], '%Y-%m-%d %H:%M:%S'),
                      participants=request_data.get('participants'))
        db.session.add(new_event)
        db.session.commit()

        return jsonify({'message': 'Event scheduled successfully'}), HTTP_CREATED

    except ValueError as e:
        return jsonify({'error': str(e)}), HTTP_BAD_REQUEST

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error. Duplicate entry or other integrity violation.'}), HTTP_BAD_REQUEST

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_INTERNAL_SERVER_ERROR

@app.route('/api/events', methods=['GET'])
def get_all_events():
    location = request.args.get('location')
    venue = request.args.get('venue')
    query = Event.query
    if location:
        query = query.filter(Event.location == location)

    if venue:
        query = query.filter(Event.venue == venue)

    events = query.all()    
    serialized_events = [event.as_dict() for event in events]
    return jsonify({'events': serialized_events})

@app.route('/api/event/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_HTTP_NOT_FOUND(event_id)
    event_details = event.as_dict()
    return jsonify({'event': event_details})


@app.route('/api/event/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.get_or_HTTP_NOT_FOUND(event_id)
        request_data = request.get_json()
        validate_event_data(request_data)

        event.title = request_data.get('title', event.title)
        event.location = request_data.get('location', event.location)
        event.venue = request_data.get('venue', event.venue)
        event.participants = request_data.get('participants', event.participants)
        event.startDate = datetime.strptime(request_data['startDate'], '%Y-%m-%d %H:%M:%S')

        db.session.commit()
        return jsonify({'message': 'Event updated successfully'})

    except ValueError as e:
        return jsonify({'error': str(e)}), HTTP_BAD_REQUEST

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error. Duplicate entry or other integrity violation.'}), HTTP_BAD_REQUEST

    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_INTERNAL_SERVER_ERROR
    

@app.route('/api/event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_HTTP_NOT_FOUND(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'})

@app.route('/api/events/sort/<string:sort_by>', methods=['GET'])
def sort_events(sort_by):
    valid_sort_fields = ['startDate', 'participants', 'createDate']

    if sort_by not in valid_sort_fields:
        return jsonify({'error': 'Invalid sort field'}), HTTP_BAD_REQUEST

    events = Event.query.order_by(getattr(Event, sort_by)).all()
    serialized_events = [event.as_dict() for event in events]
    return jsonify({'event': serialized_events})

@app.route('/api/events', methods=['POST'])
def create_events():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of events.'}), HTTP_BAD_REQUEST

    created_events = []

    for event_data in data:
        new_event = Event(title=event_data.get('title'),
                          location=event_data.get('location'),
                          venue=event_data.get('venue'),
                          participants=event_data.get('participants'),
                          startDate=datetime.strptime(event_data['startDate'], '%Y-%m-%d %H:%M:%S'))

        db.session.add(new_event)
        db.session.commit()
        created_events.append({
            'id': new_event.id,
            'message': 'Event scheduled successfully'
        })
    return jsonify({'events': created_events}), HTTP_CREATED

@app.route('/api/events', methods=['PUT'])
def update_events():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of events.'}), HTTP_BAD_REQUEST

    updated_events = []
    for event_data in data:
        event_id = event_data.get('id')

        if event_id is None:
            return jsonify({'error': 'Each event in the batch must have an "id" field.'}), HTTP_BAD_REQUEST

        event = Event.query.get_or_HTTP_NOT_FOUND(event_id)
        event.title = event_data.get('title', event.title)
        event.location = event_data.get('location', event.location)
        event.venue = event_data.get('venue', event.venue)
        event.participants = event_data.get('participants', event.participants)
        event.startDate = datetime.strptime(event_data['startDate'], '%Y-%m-%d %H:%M:%S')

        db.session.commit()
        updated_events.append({'id': event.id, 'message': 'Event updated successfully'})

    return jsonify({'events': updated_events})

@app.route('/api/events', methods=['DELETE'])
def delete_events():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of event IDs.'}), HTTP_BAD_REQUEST

    deleted_events = []
    for event_id in data:
        event = Event.query.get_or_HTTP_NOT_FOUND(event_id)
        db.session.delete(event)
        deleted_events.append({'id': event.id, 'message': 'Event deleted successfully'})

    db.session.commit()

    return jsonify({'events': deleted_events})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        thread = threading.Thread(target=remindManager, args=(), daemon=True)
        thread.start()
        app.run(debug=True)
