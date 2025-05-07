from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
products = {}
orders = {}
customers = {}
product_id_counter = 1
order_id_counter = 1
customer_id_counter = 1

# Helper function to simulate external API calls
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

# Validation functions
def validate_product(data):
    if 'name' not in data or 'price' not in data:
        abort(400, description="Product must have 'name' and 'price'")
    return data

def validate_order(data):
    if 'customerId' not in data or 'items' not in data:
        abort(400, description="Order must have 'customerId' and 'items'")
    return data

def validate_customer(data):
    if 'name' not in data or 'email' not in data:
        abort(400, description="Customer must have 'name' and 'email'")
    return data

# Products endpoints
@app.route('/products', methods=['GET'])
async def get_products():
    # Log action via external service (mock)
    await call_mock_service("GET", "posts")
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
    validate_product(data)
    new_id = str(product_id_counter)
    product_id_counter += 1
    data['id'] = new_id
    products[new_id] = data
    # Simulate posting to an inventory system via external API
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/products/<string:productId>', methods=['PUT'])
async def update_product(productId):
    if productId not in products:
        abort(404, description="Product not found")
    data = await request.get_json()
    validate_product(data)
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
    await call_mock_service("GET", "comments")
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
    validate_order(data)
    new_id = str(order_id_counter)
    order_id_counter += 1
    data['id'] = new_id
    orders[new_id] = data
    # Simulate external payment processing
    await call_mock_service("POST", "comments", data)
    return jsonify(data), 201

@app.route('/orders/<string:orderId>', methods=['PUT'])
async def update_order(orderId):
    if orderId not in orders:
        abort(404, description="Order not found")
    data = await request.get_json()
    validate_order(data)
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
    await call_mock_service("GET", "users")
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
    validate_customer(data)
    new_id = str(customer_id_counter)
    customer_id_counter += 1
    data['id'] = new_id
    customers[new_id] = data
    # Simulate external customer verification
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

@app.route('/customers/<string:customerId>', methods=['PUT'])
async def update_customer(customerId):
    if customerId not in customers:
        abort(404, description="Customer not found")
    data = await request.get_json()
    validate_customer(data)
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
