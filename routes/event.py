from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify
from const_params.const import HTTP_BAD_REQUEST, HTTP_CREATED, HTTP_INTERNAL_SERVER_ERROR, HTTP_NOT_FOUND, HTTP_OK
from validation import validate_event_data
from models import Event, User
from database import db
from datetime import datetime
from modules import limiter
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules import notify_subscribers, notify_subscribers_ws

event_page = Blueprint('event_page', __name__, template_folder='routes')

@event_page.route('/api/event/<int:event_id>', methods=['GET'])
@limiter.limit("5 per minute")
def get_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), HTTP_NOT_FOUND 
    event_details = event.as_dict()
    return jsonify({'event': event_details})


@event_page.route('/api/event/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), HTTP_NOT_FOUND 
        request_data = request.get_json()
        validate_event_data(request_data)

        for key, value in request_data.items():
            if key == 'startDate':
                setattr(event, key, datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))
            else:
                setattr(event, key, value)
        db.session.commit()

        #notifyAllSucscribers
        notify_subscribers(event_id, event.subscribers.all(), 'updated')
        notify_subscribers_ws(event_id, 'updated')
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
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), HTTP_NOT_FOUND 
    
    #notifyAllSucscribers
    notify_subscribers(event_id, event.subscribers.all(), 'deleted')
    notify_subscribers_ws(event_id, 'deleted')
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'})


@event_page.route('/api/event', methods=['POST'])
def schedule_event():
    try:
        request_data = request.get_json(force=True)
        validate_event_data(request_data)
        new_event_data = {
        'title': request_data['title'],
        'location': request_data.get('location'),
        'venue': request_data.get('venue'),
        'startDate': datetime.strptime(request_data['startDate'], '%Y-%m-%d %H:%M:%S'),
        'participants': request_data.get('participants')
        }

        new_event = Event(**new_event_data)
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


@event_page.route('/api/event/subscribe/<int:event_id>', methods=['POST'])
@jwt_required()
def subscribe_event(event_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), HTTP_NOT_FOUND

    event = Event.query.get(event_id)

    if not event:
        return jsonify({"message": "Event not found"}), HTTP_NOT_FOUND

    if user not in event.subscribers:
        event.subscribers.append(user)
        db.session.commit()
        return jsonify({"message": "Subscribed to the event"}), HTTP_OK
    else:
        return jsonify({"message": "Already subscribed to the event"}), HTTP_OK
   
@event_page.route('/api/event/unsubscribe/<int:event_id>', methods=['POST'])
@jwt_required()
def unsubscribe_event(event_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), HTTP_NOT_FOUND

    event = Event.query.get(event_id)

    if not event:
        return jsonify({"message": "Event not found"}), HTTP_NOT_FOUND

    if user in event.subscribers:
        event.subscribers.remove(user)
        db.session.commit()
        return jsonify({"message": "Unsubscribed to the event"}), HTTP_OK
    else:
        return jsonify({"message": "User is not subscribed to this event"}), HTTP_OK