from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
flights = {}
flight_bookings = {}
hotels = {}
hotel_bookings = {}
cars = {}
car_bookings = {}

flight_id_counter = 1
flight_booking_id_counter = 1
hotel_id_counter = 1
hotel_booking_id_counter = 1
car_id_counter = 1
car_booking_id_counter = 1

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

def validate_flight(data):
    if 'origin' not in data or 'destination' not in data or 'date' not in data:
        abort(400, description="Flight must have 'origin', 'destination', and 'date'")
    return data

def validate_booking(data):
    if 'userId' not in data:
        abort(400, description="Booking must have 'userId'")
    return data

# Flights endpoints
@app.route('/flights', methods=['GET'])
async def get_flights():
    await call_mock_service("GET", "posts")
    return jsonify(list(flights.values()))

@app.route('/flights/<string:flightId>', methods=['GET'])
async def get_flight(flightId):
    flight = flights.get(flightId)
    if not flight:
        abort(404, description="Flight not found")
    return jsonify(flight)

@app.route('/flights/bookings', methods=['POST'])
async def book_flight():
    global flight_booking_id_counter
    data = await request.get_json()
    validate_booking(data)
    new_id = str(flight_booking_id_counter)
    flight_booking_id_counter += 1
    data['id'] = new_id
    flight_bookings[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

# Hotels endpoints
@app.route('/hotels', methods=['GET'])
async def get_hotels():
    await call_mock_service("GET", "posts")
    return jsonify(list(hotels.values()))

@app.route('/hotels/<string:hotelId>', methods=['GET'])
async def get_hotel(hotelId):
    hotel = hotels.get(hotelId)
    if not hotel:
        abort(404, description="Hotel not found")
    return jsonify(hotel)

@app.route('/hotels/bookings', methods=['POST'])
async def book_hotel():
    global hotel_booking_id_counter
    data = await request.get_json()
    validate_booking(data)
    new_id = str(hotel_booking_id_counter)
    hotel_booking_id_counter += 1
    data['id'] = new_id
    hotel_bookings[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

# Car Rentals endpoints
@app.route('/cars', methods=['GET'])
async def get_cars():
    await call_mock_service("GET", "posts")
    return jsonify(list(cars.values()))

@app.route('/cars/bookings', methods=['POST'])
async def book_car():
    global car_booking_id_counter
    data = await request.get_json()
    validate_booking(data)
    new_id = str(car_booking_id_counter)
    car_booking_id_counter += 1
    data['id'] = new_id
    car_bookings[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

if __name__ == '__main__':
    app.run()
