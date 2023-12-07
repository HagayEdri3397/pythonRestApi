from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from validation.validationService import validate_event_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
db = SQLAlchemy(app)

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


def send_reminder(event_id, title):
    print(f"Reminder for event '{title}' with ID {event_id}: The event is starting in 30 minutes!")
    
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

        return jsonify({'message': 'Event scheduled successfully'}), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error. Duplicate entry or other integrity violation.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    event_details = event.as_dict()
    return jsonify({'event': event_details})


def update_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
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
        return jsonify({'error': str(e)}), 400

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error. Duplicate entry or other integrity violation.'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'})

def sort_events(sort_by):
    valid_sort_fields = ['startDate', 'participants', 'createDate']

    if sort_by not in valid_sort_fields:
        return jsonify({'error': 'Invalid sort field'}), 400

    events = Event.query.order_by(getattr(Event, sort_by)).all()
    serialized_events = [event.as_dict() for event in events]
    return jsonify({'event': serialized_events})


