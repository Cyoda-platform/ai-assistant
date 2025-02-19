# library_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Books endpoints
@app.route('/books', methods=['GET'])
async def get_books():
    return jsonify([])

@app.route('/books/<string:bookId>', methods=['GET'])
async def get_book(bookId):
    return jsonify({"id": bookId, "title": "The Great Gatsby"})

@app.route('/books', methods=['POST'])
async def create_book():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/books/<string:bookId>', methods=['PUT'])
async def update_book(bookId):
    data = await request.get_json()
    return jsonify({"id": bookId, **data})

@app.route('/books/<string:bookId>', methods=['DELETE'])
async def delete_book(bookId):
    return '', 204

# Authors endpoints
@app.route('/authors', methods=['GET'])
async def get_authors():
    return jsonify([])

@app.route('/authors/<string:authorId>', methods=['GET'])
async def get_author(authorId):
    return jsonify({"id": authorId, "name": "F. Scott Fitzgerald"})

@app.route('/authors', methods=['POST'])
async def create_author():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/authors/<string:authorId>', methods=['PUT'])
async def update_author(authorId):
    data = await request.get_json()
    return jsonify({"id": authorId, **data})

@app.route('/authors/<string:authorId>', methods=['DELETE'])
async def delete_author(authorId):
    return '', 204

# Borrowers endpoints
@app.route('/borrowers', methods=['GET'])
async def get_borrowers():
    return jsonify([])

@app.route('/borrowers/<string:borrowerId>', methods=['GET'])
async def get_borrower(borrowerId):
    return jsonify({"id": borrowerId, "name": "John Doe"})

@app.route('/borrowers', methods=['POST'])
async def create_borrower():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/borrowers/<string:borrowerId>', methods=['PUT'])
async def update_borrower(borrowerId):
    data = await request.get_json()
    return jsonify({"id": borrowerId, **data})

@app.route('/borrowers/<string:borrowerId>', methods=['DELETE'])
async def delete_borrower(borrowerId):
    return '', 204

# Transactions endpoints
@app.route('/transactions', methods=['GET'])
async def get_transactions():
    return jsonify([])

@app.route('/transactions', methods=['POST'])
async def create_transaction():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/transactions/<string:transactionId>', methods=['PUT'])
async def update_transaction(transactionId):
    data = await request.get_json()
    return jsonify({"id": transactionId, **data})

if __name__ == '__main__':
    app.run()
