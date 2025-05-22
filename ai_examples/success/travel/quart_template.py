# travel_booking_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)


# Flights endpoints
@app.route('/flights', methods=['GET'])
async def get_flights():
    return jsonify([])


@app.route('/flights/<string:flightId>', methods=['GET'])
async def get_flight(flightId):
    return jsonify({"id": flightId, "details": "Flight details"})


@app.route('/flights/bookings', methods=['POST'])
async def book_flight():
    data = await request.get_json()
    return jsonify(data), 201


# Hotels endpoints
@app.route('/hotels', methods=['GET'])
async def get_hotels():
    return jsonify([])


@app.route('/hotels/<string:hotelId>', methods=['GET'])
async def get_hotel(hotelId):
    return jsonify({"id": hotelId, "details": "Hotel details"})


@app.route('/hotels/bookings', methods=['POST'])
async def book_hotel():
    data = await request.get_json()
    return jsonify(data), 201


# Car Rentals endpoints
@app.route('/cars', methods=['GET'])
async def get_cars():
    return jsonify([])


@app.route('/cars/bookings', methods=['POST'])
async def book_car():
    data = await request.get_json()
    return jsonify(data), 201


if __name__ == '__main__':
    app.run()
