# ecommerce_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
products = {}
orders = {}
customers = {}
product_id_counter = 1
order_id_counter = 1
customer_id_counter = 1

# Products endpoints
@app.route('/products', methods=['GET'])
async def get_products():
    return jsonify(list(products.values()))

@app.route('/products/<string:productId>', methods=['GET'])
async def get_product(productId):
    product = products.get(productId)
    if not product:
        abort(404, description="Product not found")
    return jsonify(product)

@app.route('/products', methods=['POST'])
async def create_product():
    global product_id_counter
    data = await request.get_json()
    new_id = str(product_id_counter)
    product_id_counter += 1
    data['id'] = new_id
    products[new_id] = data
    return jsonify(data), 201

@app.route('/products/<string:productId>', methods=['PUT'])
async def update_product(productId):
    if productId not in products:
        abort(404, description="Product not found")
    data = await request.get_json()
    data['id'] = productId
    products[productId] = data
    return jsonify(data)

@app.route('/products/<string:productId>', methods=['DELETE'])
async def delete_product(productId):
    if productId not in products:
        abort(404, description="Product not found")
    del products[productId]
    return '', 204

# Orders endpoints
@app.route('/orders', methods=['GET'])
async def get_orders():
    return jsonify(list(orders.values()))

@app.route('/orders/<string:orderId>', methods=['GET'])
async def get_order(orderId):
    order = orders.get(orderId)
    if not order:
        abort(404, description="Order not found")
    return jsonify(order)

@app.route('/orders', methods=['POST'])
async def create_order():
    global order_id_counter
    data = await request.get_json()
    new_id = str(order_id_counter)
    order_id_counter += 1
    data['id'] = new_id
    orders[new_id] = data
    return jsonify(data), 201

@app.route('/orders/<string:orderId>', methods=['PUT'])
async def update_order(orderId):
    if orderId not in orders:
        abort(404, description="Order not found")
    data = await request.get_json()
    data['id'] = orderId
    orders[orderId] = data
    return jsonify(data)

@app.route('/orders/<string:orderId>', methods=['DELETE'])
async def delete_order(orderId):
    if orderId not in orders:
        abort(404, description="Order not found")
    del orders[orderId]
    return '', 204

# Customers endpoints
@app.route('/customers', methods=['GET'])
async def get_customers():
    return jsonify(list(customers.values()))

@app.route('/customers/<string:customerId>', methods=['GET'])
async def get_customer(customerId):
    customer = customers.get(customerId)
    if not customer:
        abort(404, description="Customer not found")
    return jsonify(customer)

@app.route('/customers', methods=['POST'])
async def create_customer():
    global customer_id_counter
    data = await request.get_json()
    new_id = str(customer_id_counter)
    customer_id_counter += 1
    data['id'] = new_id
    customers[new_id] = data
    return jsonify(data), 201

@app.route('/customers/<string:customerId>', methods=['PUT'])
async def update_customer(customerId):
    if customerId not in customers:
        abort(404, description="Customer not found")
    data = await request.get_json()
    data['id'] = customerId
    customers[customerId] = data
    return jsonify(data)

@app.route('/customers/<string:customerId>', methods=['DELETE'])
async def delete_customer(customerId):
    if customerId not in customers:
        abort(404, description="Customer not found")
    del customers[customerId]
    return '', 204

if __name__ == '__main__':
    app.run()
