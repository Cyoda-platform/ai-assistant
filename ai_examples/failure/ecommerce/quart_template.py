# ecommerce_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Products endpoints
@app.route('/products', methods=['GET'])
async def get_products():
    return jsonify([{"id": "1", "name": "Wireless Mouse"}])

@app.route('/products/<string:productId>', methods=['GET'])
async def get_product(productId):
    return jsonify({"id": productId, "name": "Wireless Mouse"})

@app.route('/products', methods=['POST'])
async def create_product():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/products/<string:productId>', methods=['PUT'])
async def update_product(productId):
    data = await request.get_json()
    return jsonify({"id": productId, **data})

@app.route('/products/<string:productId>', methods=['DELETE'])
async def delete_product(productId):
    return '', 204

# Orders endpoints
@app.route('/orders', methods=['GET'])
async def get_orders():
    return jsonify([])

@app.route('/orders/<string:orderId>', methods=['GET'])
async def get_order(orderId):
    return jsonify({"id": orderId})

@app.route('/orders', methods=['POST'])
async def create_order():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/orders/<string:orderId>', methods=['PUT'])
async def update_order(orderId):
    data = await request.get_json()
    return jsonify({"id": orderId, **data})

@app.route('/orders/<string:orderId>', methods=['DELETE'])
async def delete_order(orderId):
    return '', 204

# Customers endpoints
@app.route('/customers', methods=['GET'])
async def get_customers():
    return jsonify([])

@app.route('/customers/<string:customerId>', methods=['GET'])
async def get_customer(customerId):
    return jsonify({"id": customerId})

@app.route('/customers', methods=['POST'])
async def create_customer():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/customers/<string:customerId>', methods=['PUT'])
async def update_customer(customerId):
    data = await request.get_json()
    return jsonify({"id": customerId, **data})

@app.route('/customers/<string:customerId>', methods=['DELETE'])
async def delete_customer(customerId):
    return '', 204

if __name__ == '__main__':
    app.run()
