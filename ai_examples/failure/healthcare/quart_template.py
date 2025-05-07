# healthcare_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Patients endpoints
@app.route('/patients', methods=['GET'])
async def get_patients():
    return jsonify([])

@app.route('/patients/<string:patientId>', methods=['GET'])
async def get_patient(patientId):
    return jsonify({"id": patientId, "firstName": "Alice", "lastName": "Smith"})

@app.route('/patients', methods=['POST'])
async def create_patient():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/patients/<string:patientId>', methods=['PUT'])
async def update_patient(patientId):
    data = await request.get_json()
    return jsonify({"id": patientId, **data})

@app.route('/patients/<string:patientId>', methods=['DELETE'])
async def delete_patient(patientId):
    return '', 204

# Appointments endpoints
@app.route('/appointments', methods=['GET'])
async def get_appointments():
    return jsonify([])

@app.route('/appointments/<string:appointmentId>', methods=['GET'])
async def get_appointment(appointmentId):
    return jsonify({"id": appointmentId})

@app.route('/appointments', methods=['POST'])
async def create_appointment():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/appointments/<string:appointmentId>', methods=['PUT'])
async def update_appointment(appointmentId):
    data = await request.get_json()
    return jsonify({"id": appointmentId, **data})

@app.route('/appointments/<string:appointmentId>', methods=['DELETE'])
async def delete_appointment(appointmentId):
    return '', 204

if __name__ == '__main__':
    app.run()
