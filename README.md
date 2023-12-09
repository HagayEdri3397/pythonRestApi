# PythonRestApi
Rest api for alfabet

## Table of Contents
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [API Documentation](#API-Documentation)
  - [CreateNewEvent](#Schedule a new event)
  - [GetAnEvent](#Get a specific event)
  - [GetAnUnExsitEvent](#Get a non-existent event)
  - [DeleteAnEvent](#Delete an event)
  - [UpdateAnEvent](#Change a event)
  - [GetAllEvents](#Get list of events)
  - [CreateMultipleEvents](#Create a batch of events)
  - [UpdateMultipleEvents](#Change a batch of events)
  - [DeleteMultipleEvents](#Delete a batch of events)
  - [SortEvents](#Sort events by 'startDate', 'participants', 'createDate')
  
  

## Setup Instructions

### Prerequisites
Make sure you have the following installed on your machine:
- Python (version 3.10.3)
- pip (Python package installer)
- [Virtualenv](https://virtualenv.pypa.io/) (optional but recommended)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/HagayEdri3397/pythonRestApi.git
   cd pythonRestApi
   ```
   
2. Create and activate a virtual environment (optional but recommended):
```
virtualenv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Run the Flask application:
```
python app.py
```


# API-Documentation

## Schedule a new event

### Request

`POST /api/event`

    curl -i -H 'Accept: application/json' http://localhost:5000/api/event
	
	Body:
{
	"title": "new party",
	"location": "Tel aviv",
	"venue": "Habima",
	"startDate": "2023-12-10 21:23:00",
    "participants": "300"
}


### Response

    HTTP/1.1 201 Created
    Status: 201 Created
    Content-Type: application/json

    {
		"message": "Event scheduled successfully"
	}

## Get a specific event

### Request

`GET /api/event/id`

    curl -i -H 'Accept: application/json' http://localhost:7000/api/event/1

### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Connection: close
    Content-Type: application/json

    {
    "event": {
        "createDate": "2023-12-09 19:37:33",
        "id": 1,
        "location": "Tel aviv",
        "participants": 300,
        "startDate": "2023-12-09 21:23:00",
        "title": "new party",
        "venue": "Habima"
    }
}

## Get a non-existent event

### Request

`GET /api/event/id`

    curl -i -H 'Accept: application/json' http://localhost:5000/api/event/9999

### Response

    HTTP/1.1 404 Not Found
    Status: 404 Not Found
    Connection: close
    Content-Type: application/json


## Delete an event

### Request

`DELETE /api/event/id`

    curl -i -H 'Accept: application/json' -X DELETE http://localhost:5000/api/event/1
	
### Response

    HTTP/1.1 200 OK
    Status: 200 PK
    Content-Type: application/json

    {
		"message": "Event deleted successfully"
	}

## Change a event

### Request

`PUT /api/event/id'

    curl -i -H 'Accept: application/json' -X PUT -d http://localhost:5000/api/event/1

Body:
{
	"title": "new party",
	"location": "Tel aviv",
	"venue": "Habima",
	"startDate": "2023-12-10 21:30:00",
    "participants": "400"
}

### Response

    HTTP/1.1 200 OK
    Status: 200 PK
    Content-Type: application/json

    {
		"message": "Event updated successfully"
	}
	
## Get list of events 

### Request

`GET /api/events?location=value&venue=value`

    curl -i -H 'Accept: application/json' http://localhost:5000/api/events

### Description
location & venue are optional parameters
### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Connection: close
    Content-Type: application/json

    {
    "events": [
        {
            "createDate": "2023-12-09 18:03:49",
            "id": 1,
            "location": "Tel aviv",
            "participants": 300,
            "startDate": "2023-12-10 21:23:00",
            "title": "new event",
            "venue": "Habima"
        },
        {
            "createDate": "2023-12-09 19:37:33",
            "id": 2,
            "location": "Tel aviv",
            "participants": 400,
            "startDate": "2023-12-10 21:30:00",
            "title": "new party",
            "venue": "Habima"
        }
    ]
}


## Create a batch of events

### Request

`POST /api/events`

    curl -i -H 'Accept: application/json' -X POST http://localhost:5000/api/events`
	
	Body
	[{
	"title": "new event",
	"location": "tel aviv",
	"venue": "habima",
	"startDate": "2023-12-09 21:23:00",
    "participants": "100"
},
{
	"title": "new event2",
	"location": "tel aviv",
	"venue": "habima",
	"startDate": "2023-12-09 21:23:00",
    "participants": "200"
}]

### Response

    HTTP/1.1 201 Created
    Status: 201 Created
    Connection: close
    Content-Type: application/json

{
    "events": [
        {
            "id": 5,
            "message": "Event scheduled successfully"
        },
        {
            "id": 6,
            "message": "Event scheduled successfully"
        }
    ]
}


## Change a batch of events

### Request

`PUT /api/events`

    curl -i -H 'Accept: application/json' -X PUT http://localhost:5000/api/events`
	
	Body
	[{
	"id": 1,
	"title": "new event update",
	"location": "tel aviv",
	"venue": "habima",
	"startDate": "2023-12-09 21:23:00",
    "participants": "100"
},
{
	"id": 3,
	"title": "new event2 update",
	"location": "tel aviv",
	"venue": "habima",
	"startDate": "2023-12-09 21:23:00",
    "participants": "200"
}]

### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Connection: close
    Content-Type: application/json

    {
    "events": [
        {
            "id": 1,
            "message": "Event updated successfully"
        },
        {
            "id": 3,
            "message": "Event updated successfully"
        }
    ]
}

## Delete a batch of events

### Request

`DELETE /api/events`

    curl -i -H 'Accept: application/json' -X DELETE http://localhost:5000/api/events`
	
	Body
	[5,6]
	
### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Connection: close
    Content-Type: application/json

{
    "events": [
        {
            "id": 5,
            "message": "Event deleted successfully"
        },
        {
            "id": 6,
            "message": "Event deleted successfully"
        }
    ]
}

## Sort events by 'startDate', 'participants', 'createDate'

### Request

`GET /api/events/sort/sort_by`

    curl -i -H 'Accept: application/json' -X GET http://localhost:5000/events/sort/sort_by`
	
### Response

    HTTP/1.1 200 OK
    Status: 200 OK
    Connection: close
    Content-Type: application/json

{
    "event": [
        {
            "createDate": "2023-12-09 18:03:49",
            "id": 1,
            "location": "tel aviv",
            "participants": 100,
            "startDate": "2023-12-09 21:20:00",
            "title": "new event",
            "venue": "habima"
        },
        {
            "createDate": "2023-12-09 19:37:33",
            "id": 3,
            "location": "tel aviv",
            "participants": 200,
            "startDate": "2023-12-09 21:23:00",
            "title": "new event2 update",
            "venue": "habima"
        },
        {
            "createDate": "2023-12-09 20:27:32",
            "id": 4,
            "location": "habima",
            "participants": 302,
            "startDate": "2023-12-10 21:23:00",
            "title": "new event",
            "venue": "5"
        }
    ]
}


