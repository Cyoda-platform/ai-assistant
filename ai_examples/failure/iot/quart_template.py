# iot_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Devices endpoints
@app.route('/devices', methods=['GET'])
async def get_devices():
    return jsonify([])

@app.route('/devices/<string:deviceId>', methods=['GET'])
async def get_device(deviceId):
    return jsonify({"id": deviceId, "name": "Temperature Sensor"})

@app.route('/devices', methods=['POST'])
async def create_device():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/devices/<string:deviceId>', methods=['PUT'])
async def update_device(deviceId):
    data = await request.get_json()
    return jsonify({"id": deviceId, **data})

@app.route('/devices/<string:deviceId>', methods=['DELETE'])
async def delete_device(deviceId):
    return '', 204

# Configurations endpoints
@app.route('/devices/<string:deviceId>/config', methods=['GET'])
async def get_device_config(deviceId):
    return jsonify({"deviceId": deviceId, "config": {}})

@app.route('/devices/<string:deviceId>/config', methods=['PUT'])
async def update_device_config(deviceId):
    data = await request.get_json()
    return jsonify({"deviceId": deviceId, "config": data})

if __name__ == '__main__':
    app.run()
