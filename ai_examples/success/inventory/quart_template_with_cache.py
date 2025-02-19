# inventory_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
items = {}
warehouses = {}
movements = {}

item_id_counter = 1
warehouse_id_counter = 1
movement_id_counter = 1

# Items endpoints
@app.route('/items', methods=['GET'])
async def get_items():
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
    new_id = str(item_id_counter)
    item_id_counter += 1
    data['id'] = new_id
    items[new_id] = data
    return jsonify(data), 201

@app.route('/items/<string:itemId>', methods=['PUT'])
async def update_item(itemId):
    if itemId not in items:
        abort(404, description="Item not found")
    data = await request.get_json()
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
    new_id = str(warehouse_id_counter)
    warehouse_id_counter += 1
    data['id'] = new_id
    warehouses[new_id] = data
    return jsonify(data), 201

@app.route('/warehouses/<string:warehouseId>', methods=['PUT'])
async def update_warehouse(warehouseId):
    if warehouseId not in warehouses:
        abort(404, description="Warehouse not found")
    data = await request.get_json()
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
    return jsonify(list(movements.values()))

@app.route('/movements', methods=['POST'])
async def create_movement():
    global movement_id_counter
    data = await request.get_json()
    new_id = str(movement_id_counter)
    movement_id_counter += 1
    data['id'] = new_id
    movements[new_id] = data
    return jsonify(data), 201

if __name__ == '__main__':
    app.run()
