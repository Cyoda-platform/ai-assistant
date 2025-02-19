# iot_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
devices = {}
device_configs = {}

device_id_counter = 1

# Devices endpoints
@app.route('/devices', methods=['GET'])
async def get_devices():
    return jsonify(list(devices.values()))

@app.route('/devices/<string:deviceId>', methods=['GET'])
async def get_device(deviceId):
    device = devices.get(deviceId)
    if not device:
        abort(404, description="Device not found")
    return jsonify(device)

@app.route('/devices', methods=['POST'])
async def create_device():
    global device_id_counter
    data = await request.get_json()
    new_id = str(device_id_counter)
    device_id_counter += 1
    data['id'] = new_id
    devices[new_id] = data
    # Initialize config as empty
    device_configs[new_id] = {}
    return jsonify(data), 201

@app.route('/devices/<string:deviceId>', methods=['PUT'])
async def update_device(deviceId):
    if deviceId not in devices:
        abort(404, description="Device not found")
    data = await request.get_json()
    data['id'] = deviceId
    devices[deviceId] = data
    return jsonify(data)

@app.route('/devices/<string:deviceId>', methods=['DELETE'])
async def delete_device(deviceId):
    if deviceId not in devices:
        abort(404, description="Device not found")
    del devices[deviceId]
    if deviceId in device_configs:
        del device_configs[deviceId]
    return '', 204

# Configurations endpoints
@app.route('/devices/<string:deviceId>/config', methods=['GET'])
async def get_device_config(deviceId):
    if deviceId not in devices:
        abort(404, description="Device not found")
    return jsonify({"deviceId": deviceId, "config": device_configs.get(deviceId, {})})

@app.route('/devices/<string:deviceId>/config', methods=['PUT'])
async def update_device_config(deviceId):
    if deviceId not in devices:
        abort(404, description="Device not found")
    data = await request.get_json()
    device_configs[deviceId] = data
    return jsonify({"deviceId": deviceId, "config": data})

if __name__ == '__main__':
    app.run()
