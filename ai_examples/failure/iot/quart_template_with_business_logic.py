from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
devices = {}
device_configs = {}

device_id_counter = 1

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

def validate_device(data):
    if 'name' not in data or 'model' not in data:
        abort(400, description="Device must have 'name' and 'model'")
    return data

# Devices endpoints
@app.route('/devices', methods=['GET'])
async def get_devices():
    await call_mock_service("GET", "posts")
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
    validate_device(data)
    new_id = str(device_id_counter)
    device_id_counter += 1
    data['id'] = new_id
    devices[new_id] = data
    device_configs[new_id] = {}  # Initialize empty config
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/devices/<string:deviceId>', methods=['PUT'])
async def update_device(deviceId):
    if deviceId not in devices:
        abort(404, description="Device not found")
    data = await request.get_json()
    validate_device(data)
    data['id'] = deviceId
    devices[deviceId] = data
    return jsonify(data)

@app.route('/devices/<string:deviceId>', methods=['DELETE'])
async def delete_device(deviceId):
    if deviceId not in devices:
        abort(404, description="Device not found")
    del devices[deviceId]
    device_configs.pop(deviceId, None)
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
    await call_mock_service("POST", "posts", data)
    return jsonify({"deviceId": deviceId, "config": data})

if __name__ == '__main__':
    app.run()
