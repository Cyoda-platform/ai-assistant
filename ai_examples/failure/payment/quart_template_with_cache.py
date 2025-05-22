# payment_gateway_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
transactions = {}
refunds = {}
transaction_id_counter = 1

# Transactions endpoints
@app.route('/transactions', methods=['GET'])
async def get_transactions():
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
    new_id = str(transaction_id_counter)
    transaction_id_counter += 1
    data['id'] = new_id
    transactions[new_id] = data
    return jsonify(data), 201

@app.route('/transactions/<string:transactionId>', methods=['PUT'])
async def update_transaction(transactionId):
    if transactionId not in transactions:
        abort(404, description="Transaction not found")
    data = await request.get_json()
    data['id'] = transactionId
    transactions[transactionId] = data
    return jsonify(data)

# Refund endpoint
@app.route('/transactions/<string:transactionId>/refund', methods=['POST'])
async def refund_transaction(transactionId):
    if transactionId not in transactions:
        abort(404, description="Transaction not found")
    data = await request.get_json()
    refunds[transactionId] = data
    return jsonify({"transactionId": transactionId, "refund": data}), 200

# Payment Methods endpoint (static)
@app.route('/payment-methods', methods=['GET'])
async def get_payment_methods():
    methods = ["credit_card", "paypal", "bank_transfer"]
    return jsonify(methods)

if __name__ == '__main__':
    app.run()
