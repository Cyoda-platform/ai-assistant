from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
transactions = {}
refunds = {}
transaction_id_counter = 1

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

def validate_transaction(data):
    if 'amount' not in data or 'currency' not in data:
        abort(400, description="Transaction must have 'amount' and 'currency'")
    return data

# Transactions endpoints
@app.route('/transactions', methods=['GET'])
async def get_transactions():
    await call_mock_service("GET", "posts")
    return jsonify(list(transactions.values()))

@app.route('/transactions/<string:transactionId>', methods=['GET'])
async def get_transaction(transactionId):
    transaction = transactions.get(transactionId)
    if not transaction:
        abort(404, description="Transaction not found")
    return jsonify(transaction)

@app.route('/transactions', methods=['POST'])
async def create_transaction():
    global transaction_id_counter
    data = await request.get_json()
    validate_transaction(data)
    new_id = str(transaction_id_counter)
    transaction_id_counter += 1
    data['id'] = new_id
    transactions[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/transactions/<string:transactionId>', methods=['PUT'])
async def update_transaction(transactionId):
    if transactionId not in transactions:
        abort(404, description="Transaction not found")
    data = await request.get_json()
    validate_transaction(data)
    data['id'] = transactionId
    transactions[transactionId] = data
    return jsonify(data)

# Refund endpoint
@app.route('/transactions/<string:transactionId>/refund', methods=['POST'])
async def refund_transaction(transactionId):
    if transactionId not in transactions:
        abort(404, description="Transaction not found")
    data = await request.get_json()
    if 'amount' not in data:
        abort(400, description="Refund must include 'amount'")
    refunds[transactionId] = data
    await call_mock_service("POST", "posts", data)
    return jsonify({"transactionId": transactionId, "refund": data}), 200

# Payment Methods endpoint (static)
@app.route('/payment-methods', methods=['GET'])
async def get_payment_methods():
    methods = ["credit_card", "paypal", "bank_transfer"]
    return jsonify(methods)

if __name__ == '__main__':
    app.run()
