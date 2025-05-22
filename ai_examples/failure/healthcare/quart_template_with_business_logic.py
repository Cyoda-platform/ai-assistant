from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
patients = {}
appointments = {}

patient_id_counter = 1
appointment_id_counter = 1

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

def validate_patient(data):
    if 'firstName' not in data or 'dob' not in data:
        abort(400, description="Patient must have 'firstName' and 'dob'")
    return data

def validate_appointment(data):
    if 'patientId' not in data or 'doctorId' not in data or 'appointmentDate' not in data:
        abort(400, description="Appointment must have 'patientId', 'doctorId', and 'appointmentDate'")
    return data

# Patients endpoints
@app.route('/patients', methods=['GET'])
async def get_patients():
    await call_mock_service("GET", "posts")
    return jsonify(list(patients.values()))

@app.route('/patients/<string:patientId>', methods=['GET'])
async def get_patient(patientId):
    patient = patients.get(patientId)
    if not patient:
        abort(404, description="Patient not found")
    return jsonify(patient)

@app.route('/patients', methods=['POST'])
async def create_patient():
    global patient_id_counter
    data = await request.get_json()
    validate_patient(data)
    new_id = str(patient_id_counter)
    patient_id_counter += 1
    data['id'] = new_id
    patients[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/patients/<string:patientId>', methods=['PUT'])
async def update_patient(patientId):
    if patientId not in patients:
        abort(404, description="Patient not found")
    data = await request.get_json()
    validate_patient(data)
    data['id'] = patientId
    patients[patientId] = data
    return jsonify(data)

@app.route('/patients/<string:patientId>', methods=['DELETE'])
async def delete_patient(patientId):
    if patientId not in patients:
        abort(404, description="Patient not found")
    del patients[patientId]
    return '', 204

# Appointments endpoints
@app.route('/appointments', methods=['GET'])
async def get_appointments():
    await call_mock_service("GET", "posts")
    return jsonify(list(appointments.values()))

@app.route('/appointments/<string:appointmentId>', methods=['GET'])
async def get_appointment(appointmentId):
    appointment = appointments.get(appointmentId)
    if not appointment:
        abort(404, description="Appointment not found")
    return jsonify(appointment)

@app.route('/appointments', methods=['POST'])
async def create_appointment():
    global appointment_id_counter
    data = await request.get_json()
    validate_appointment(data)
    new_id = str(appointment_id_counter)
    appointment_id_counter += 1
    data['id'] = new_id
    appointments[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/appointments/<string:appointmentId>', methods=['PUT'])
async def update_appointment(appointmentId):
    if appointmentId not in appointments:
        abort(404, description="Appointment not found")
    data = await request.get_json()
    validate_appointment(data)
    data['id'] = appointmentId
    appointments[appointmentId] = data
    return jsonify(data)

@app.route('/appointments/<string:appointmentId>', methods=['DELETE'])
async def delete_appointment(appointmentId):
    if appointmentId not in appointments:
        abort(404, description="Appointment not found")
    del appointments[appointmentId]
    return '', 204

if __name__ == '__main__':
    app.run()
