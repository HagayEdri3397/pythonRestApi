from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify
from models import Event
from const_params.const import HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_INTERNAL_SERVER_ERROR, HTTP_NOT_FOUND
from datetime import datetime
from database import db
from validation import validate_event_data
from modules import notify_subscribers, notify_subscribers_ws

events_page = Blueprint('events_page', __name__, template_folder='routes/events')

@events_page.route('/api/events/sort/<string:sort_by>', methods=['GET'])
def sort_events(sort_by):
    valid_sort_fields = ['startDate', 'participants', 'createDate']

    if sort_by not in valid_sort_fields:
        return jsonify({'error': 'Invalid sort field'}), HTTP_BAD_REQUEST

    events = Event.query.order_by(getattr(Event, sort_by)).all()
    serialized_events = [event.as_dict() for event in events]
    return jsonify({'event': serialized_events})


@events_page.route('/api/events', methods=['POST'])
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

@events_page.route('/api/events', methods=['PUT'])
def update_events():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'error': 'Invalid data format. Expected a list of events.'}), HTTP_BAD_REQUEST

        updated_events = []
        for event_data in data:
            event_id = event_data.get('id')

            if event_id is None:
                return jsonify({'error': 'Each event in the batch must have an "id" field.'}), HTTP_BAD_REQUEST
            
            validate_event_data(event_data)
            event = Event.query.get(event_id)
            if not event:
                updated_events.append({'id': event_id, 'error': 'Event not found'})
                continue
            event.title = event_data.get('title', event.title)
            event.location = event_data.get('location', event.location)
            event.venue = event_data.get('venue', event.venue)
            event.participants = event_data.get('participants', event.participants)
            event.startDate = datetime.strptime(event_data['startDate'], '%Y-%m-%d %H:%M:%S')
            updated_events.append({'id': event.id, 'message': 'Event updated successfully'})
            
            #notifyAllSucscribers
            notify_subscribers(event_id, event.subscribers.all(), 'updated')
            notify_subscribers_ws(event_id, 'updated')
        db.session.commit()

        

        return jsonify({'events': updated_events})

    except ValueError as e:
        return jsonify({'error': str(e)}), HTTP_BAD_REQUEST
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error. Duplicate entry or other integrity violation.'}), HTTP_BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_INTERNAL_SERVER_ERROR
    

@events_page.route('/api/events', methods=['DELETE'])
def delete_events():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of event IDs.'}), HTTP_BAD_REQUEST

    deleted_events = []
    for event_id in data:
        event = Event.query.get(event_id)
        if not event:
            deleted_events.append({'id': event_id, 'error': 'Event not found'})
            continue
        db.session.delete(event)
        deleted_events.append({'id': event.id, 'message': 'Event deleted successfully'})
        
        #notifyAllSucscribers
        notify_subscribers(event_id, event.subscribers.all(), 'deleted')
        notify_subscribers_ws(event_id, 'deleted')
    db.session.commit()

    
    return jsonify({'events': deleted_events})

@events_page.route('/api/events', methods=['GET'])
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
