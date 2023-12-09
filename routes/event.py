from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify
from const_params.const import HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_INTERNAL_SERVER_ERROR
from validation.validationService import validate_event_data
from models import Event
from database import db
from datetime import datetime
from modules import limiter
event_page = Blueprint('event_page', __name__, template_folder='routes')

@event_page.route('/api/event/<int:event_id>', methods=['GET'])
@limiter.limit("5 per minute")
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    event_details = event.as_dict()
    return jsonify({'event': event_details})


@event_page.route('/api/event/<int:event_id>', methods=['PUT'])
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
    except ValueError as e:
        return jsonify({'error': str(e)}), HTTP_BAD_REQUEST
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error. Duplicate entry or other integrity violation.'}), HTTP_BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_INTERNAL_SERVER_ERROR
    return jsonify({'message': 'Event updated successfully'})


@event_page.route('/api/event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'})


@event_page.route('/api/event', methods=['POST'])
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
    except ValueError as e:
        return jsonify({'error': str(e)}), HTTP_BAD_REQUEST
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error. Duplicate entry or other integrity violation.'}), HTTP_BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_INTERNAL_SERVER_ERROR
    return jsonify({'message': 'Event scheduled successfully'}), HTTP_CREATED
