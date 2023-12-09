from flask import Blueprint, request, jsonify
from models import Event
from const_params.const import HTTP_BAD_REQUEST, HTTP_CREATED
from datetime import datetime
from database import db

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
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of events.'}), HTTP_BAD_REQUEST

    updated_events = []
    for event_data in data:
        event_id = event_data.get('id')

        if event_id is None:
            return jsonify({'error': 'Each event in the batch must have an "id" field.'}), HTTP_BAD_REQUEST

        event = Event.query.get_or_404(event_id)
        event.title = event_data.get('title', event.title)
        event.location = event_data.get('location', event.location)
        event.venue = event_data.get('venue', event.venue)
        event.participants = event_data.get('participants', event.participants)
        event.startDate = datetime.strptime(event_data['startDate'], '%Y-%m-%d %H:%M:%S')

        db.session.commit()
        updated_events.append({'id': event.id, 'message': 'Event updated successfully'})

    return jsonify({'events': updated_events})

@events_page.route('/api/events', methods=['DELETE'])
def delete_events():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of event IDs.'}), HTTP_BAD_REQUEST

    deleted_events = []
    for event_id in data:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        deleted_events.append({'id': event.id, 'message': 'Event deleted successfully'})

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
