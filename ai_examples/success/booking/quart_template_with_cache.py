# event_booking_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
events = {}
bookings = {}
event_id_counter = 1
booking_id_counter = 1

# Events endpoints
@app.route('/events', methods=['GET'])
async def get_events():
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
    new_id = str(event_id_counter)
    event_id_counter += 1
    data['id'] = new_id
    events[new_id] = data
    return jsonify(data), 201

@app.route('/events/<string:eventId>', methods=['PUT'])
async def update_event(eventId):
    if eventId not in events:
        abort(404, description="Event not found")
    data = await request.get_json()
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
    new_id = str(booking_id_counter)
    booking_id_counter += 1
    data['id'] = new_id
    data['eventId'] = eventId
    bookings[new_id] = data
    return jsonify(data), 201

@app.route('/bookings/<string:bookingId>', methods=['DELETE'])
async def delete_booking(bookingId):
    if bookingId not in bookings:
        abort(404, description="Booking not found")
    del bookings[bookingId]
    return '', 204

if __name__ == '__main__':
    app.run()
