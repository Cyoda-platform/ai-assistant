# event_booking_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Events endpoints
@app.route('/events', methods=['GET'])
async def get_events():
    return jsonify([])

@app.route('/events/<string:eventId>', methods=['GET'])
async def get_event(eventId):
    return jsonify({"id": eventId, "title": "Tech Conference 2025"})

@app.route('/events', methods=['POST'])
async def create_event():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/events/<string:eventId>', methods=['PUT'])
async def update_event(eventId):
    data = await request.get_json()
    return jsonify({"id": eventId, **data})

@app.route('/events/<string:eventId>', methods=['DELETE'])
async def delete_event(eventId):
    return '', 204

# Bookings endpoints
@app.route('/bookings', methods=['GET'])
async def get_bookings():
    return jsonify([])

@app.route('/bookings/<string:bookingId>', methods=['GET'])
async def get_booking(bookingId):
    return jsonify({"id": bookingId})

@app.route('/events/<string:eventId>/bookings', methods=['POST'])
async def create_booking(eventId):
    data = await request.get_json()
    return jsonify({"eventId": eventId, **data}), 201

@app.route('/bookings/<string:bookingId>', methods=['DELETE'])
async def delete_booking(bookingId):
    return '', 204

if __name__ == '__main__':
    app.run()
