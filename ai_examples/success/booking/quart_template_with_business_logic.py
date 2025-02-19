from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
events = {}
bookings = {}
event_id_counter = 1
booking_id_counter = 1

async def call_mock_service(operation, resource, data=None):
    url = f"https://jsonplaceholder.typicode.com/{resource}"
    async with httpx.AsyncClient() as client:
        if operation == "GET":
            response = await client.get(url)
        elif operation == "POST":
            response = await client.post(url, json=data)
        else:
            response = None
    return response.json() if response is not None else {}

def validate_event(data):
    if 'title' not in data or 'date' not in data:
        abort(400, description="Event must have 'title' and 'date'")
    return data

def validate_booking(data):
    if 'userId' not in data or 'tickets' not in data:
        abort(400, description="Booking must have 'userId' and 'tickets'")
    return data

# Events endpoints
@app.route('/events', methods=['GET'])
async def get_events():
    await call_mock_service("GET", "posts")
    return jsonify(list(events.values()))

@app.route('/events/<string:eventId>', methods=['GET'])
async def get_event(eventId):
    event = events.get(eventId)
    if not event:
        abort(404, description="Event not found")
    return jsonify(event)

@app.route('/events', methods=['POST'])
async def create_event():
    global event_id_counter
    data = await request.get_json()
    validate_event(data)
    new_id = str(event_id_counter)
    event_id_counter += 1
    data['id'] = new_id
    events[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/events/<string:eventId>', methods=['PUT'])
async def update_event(eventId):
    if eventId not in events:
        abort(404, description="Event not found")
    data = await request.get_json()
    validate_event(data)
    data['id'] = eventId
    events[eventId] = data
    return jsonify(data)

@app.route('/events/<string:eventId>', methods=['DELETE'])
async def delete_event(eventId):
    if eventId not in events:
        abort(404, description="Event not found")
    del events[eventId]
    return '', 204

# Bookings endpoints
@app.route('/bookings', methods=['GET'])
async def get_bookings():
    await call_mock_service("GET", "posts")
    return jsonify(list(bookings.values()))

@app.route('/bookings/<string:bookingId>', methods=['GET'])
async def get_booking(bookingId):
    booking = bookings.get(bookingId)
    if not booking:
        abort(404, description="Booking not found")
    return jsonify(booking)

@app.route('/events/<string:eventId>/bookings', methods=['POST'])
async def create_booking(eventId):
    if eventId not in events:
        abort(404, description="Event not found")
    global booking_id_counter
    data = await request.get_json()
    validate_booking(data)
    new_id = str(booking_id_counter)
    booking_id_counter += 1
    data['id'] = new_id
    data['eventId'] = eventId
    bookings[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/bookings/<string:bookingId>', methods=['DELETE'])
async def delete_booking(bookingId):
    if bookingId not in bookings:
        abort(404, description="Booking not found")
    del bookings[bookingId]
    return '', 204

if __name__ == '__main__':
    app.run()
