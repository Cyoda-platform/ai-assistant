from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
items = {}
warehouses = {}
movements = {}

item_id_counter = 1
warehouse_id_counter = 1
movement_id_counter = 1

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

def validate_item(data):
    if 'name' not in data or 'sku' not in data:
        abort(400, description="Item must have 'name' and 'sku'")
    return data

def validate_warehouse(data):
    if 'location' not in data:
        abort(400, description="Warehouse must have 'location'")
    return data

def validate_movement(data):
    if 'itemId' not in data or 'warehouseId' not in data or 'quantity' not in data:
        abort(400, description="Movement must have 'itemId', 'warehouseId', and 'quantity'")
    return data

# Items endpoints
@app.route('/items', methods=['GET'])
async def get_items():
    await call_mock_service("GET", "posts")
    return jsonify(list(items.values()))

@app.route('/items/<string:itemId>', methods=['GET'])
async def get_item(itemId):
    item = items.get(itemId)
    if not item:
        abort(404, description="Item not found")
    return jsonify(item)

@app.route('/items', methods=['POST'])
async def create_item():
    global item_id_counter
    data = await request.get_json()
    validate_item(data)
    new_id = str(item_id_counter)
    item_id_counter += 1
    data['id'] = new_id
    items[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/items/<string:itemId>', methods=['PUT'])
async def update_item(itemId):
    if itemId not in items:
        abort(404, description="Item not found")
    data = await request.get_json()
    validate_item(data)
    data['id'] = itemId
    items[itemId] = data
    return jsonify(data)

@app.route('/items/<string:itemId>', methods=['DELETE'])
async def delete_item(itemId):
    if itemId not in items:
        abort(404, description="Item not found")
    del items[itemId]
    return '', 204

# Warehouses endpoints
@app.route('/warehouses', methods=['GET'])
async def get_warehouses():
    await call_mock_service("GET", "users")
    return jsonify(list(warehouses.values()))

@app.route('/warehouses/<string:warehouseId>', methods=['GET'])
async def get_warehouse(warehouseId):
    warehouse = warehouses.get(warehouseId)
    if not warehouse:
        abort(404, description="Warehouse not found")
    return jsonify(warehouse)

@app.route('/warehouses', methods=['POST'])
async def create_warehouse():
    global warehouse_id_counter
    data = await request.get_json()
    validate_warehouse(data)
    new_id = str(warehouse_id_counter)
    warehouse_id_counter += 1
    data['id'] = new_id
    warehouses[new_id] = data
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

@app.route('/warehouses/<string:warehouseId>', methods=['PUT'])
async def update_warehouse(warehouseId):
    if warehouseId not in warehouses:
        abort(404, description="Warehouse not found")
    data = await request.get_json()
    validate_warehouse(data)
    data['id'] = warehouseId
    warehouses[warehouseId] = data
    return jsonify(data)

@app.route('/warehouses/<string:warehouseId>', methods=['DELETE'])
async def delete_warehouse(warehouseId):
    if warehouseId not in warehouses:
        abort(404, description="Warehouse not found")
    del warehouses[warehouseId]
    return '', 204

# Stock Movements endpoints
@app.route('/movements', methods=['GET'])
async def get_movements():
    await call_mock_service("GET", "posts")
    return jsonify(list(movements.values()))

@app.route('/movements', methods=['POST'])
async def create_movement():
    global movement_id_counter
    data = await request.get_json()
    validate_movement(data)
    new_id = str(movement_id_counter)
    movement_id_counter += 1
    data['id'] = new_id
    movements[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

if __name__ == '__main__':
    app.run()
