from datetime import datetime

def validate_event_data(data):
    required_fields = ['title', 'startDate', 'location', 'venue', 'participants']
    for field in required_fields:
        if field not in data:
            raise ValueError(f'Missing required field: {field}')
    validate_date(data['startDate'])

def validate_date(date):
    try:
        datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError('Invalid date format. Expected: YYYY-MM-DD HH:MM:SS')
