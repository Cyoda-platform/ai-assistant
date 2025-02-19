# payment_gateway_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Transactions endpoints
@app.route('/transactions', methods=['GET'])
async def get_transactions():
    return jsonify([])

@app.route('/transactions/<string:transactionId>', methods=['GET'])
async def get_transaction(transactionId):
    return jsonify({"id": transactionId, "amount": 99.99})

@app.route('/transactions', methods=['POST'])
async def create_transaction():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/transactions/<string:transactionId>', methods=['PUT'])
async def update_transaction(transactionId):
    data = await request.get_json()
    return jsonify({"id": transactionId, **data})

# Refund endpoint
@app.route('/transactions/<string:transactionId>/refund', methods=['POST'])
async def refund_transaction(transactionId):
    data = await request.get_json()
    return jsonify({"id": transactionId, "refund": data}), 200

# Payment Methods endpoint
@app.route('/payment-methods', methods=['GET'])
async def get_payment_methods():
    return jsonify(["credit_card", "paypal", "bank_transfer"])

if __name__ == '__main__':
    app.run()
