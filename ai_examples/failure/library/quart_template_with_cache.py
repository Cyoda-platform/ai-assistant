# library_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
books = {}
authors = {}
borrowers = {}
transactions = {}

book_id_counter = 1
author_id_counter = 1
borrower_id_counter = 1
transaction_id_counter = 1

# Books endpoints
@app.route('/books', methods=['GET'])
async def get_books():
    return jsonify(list(books.values()))

@app.route('/books/<string:bookId>', methods=['GET'])
async def get_book(bookId):
    book = books.get(bookId)
    if not book:
        abort(404, description="Book not found")
    return jsonify(book)

@app.route('/books', methods=['POST'])
async def create_book():
    global book_id_counter
    data = await request.get_json()
    new_id = str(book_id_counter)
    book_id_counter += 1
    data['id'] = new_id
    books[new_id] = data
    return jsonify(data), 201

@app.route('/books/<string:bookId>', methods=['PUT'])
async def update_book(bookId):
    if bookId not in books:
        abort(404, description="Book not found")
    data = await request.get_json()
    data['id'] = bookId
    books[bookId] = data
    return jsonify(data)

@app.route('/books/<string:bookId>', methods=['DELETE'])
async def delete_book(bookId):
    if bookId not in books:
        abort(404, description="Book not found")
    del books[bookId]
    return '', 204

# Authors endpoints
@app.route('/authors', methods=['GET'])
async def get_authors():
    return jsonify(list(authors.values()))

@app.route('/authors/<string:authorId>', methods=['GET'])
async def get_author(authorId):
    author = authors.get(authorId)
    if not author:
        abort(404, description="Author not found")
    return jsonify(author)

@app.route('/authors', methods=['POST'])
async def create_author():
    global author_id_counter
    data = await request.get_json()
    new_id = str(author_id_counter)
    author_id_counter += 1
    data['id'] = new_id
    authors[new_id] = data
    return jsonify(data), 201

@app.route('/authors/<string:authorId>', methods=['PUT'])
async def update_author(authorId):
    if authorId not in authors:
        abort(404, description="Author not found")
    data = await request.get_json()
    data['id'] = authorId
    authors[authorId] = data
    return jsonify(data)

@app.route('/authors/<string:authorId>', methods=['DELETE'])
async def delete_author(authorId):
    if authorId not in authors:
        abort(404, description="Author not found")
    del authors[authorId]
    return '', 204

# Borrowers endpoints
@app.route('/borrowers', methods=['GET'])
async def get_borrowers():
    return jsonify(list(borrowers.values()))

@app.route('/borrowers/<string:borrowerId>', methods=['GET'])
async def get_borrower(borrowerId):
    borrower = borrowers.get(borrowerId)
    if not borrower:
        abort(404, description="Borrower not found")
    return jsonify(borrower)

@app.route('/borrowers', methods=['POST'])
async def create_borrower():
    global borrower_id_counter
    data = await request.get_json()
    new_id = str(borrower_id_counter)
    borrower_id_counter += 1
    data['id'] = new_id
    borrowers[new_id] = data
    return jsonify(data), 201

@app.route('/borrowers/<string:borrowerId>', methods=['PUT'])
async def update_borrower(borrowerId):
    if borrowerId not in borrowers:
        abort(404, description="Borrower not found")
    data = await request.get_json()
    data['id'] = borrowerId
    borrowers[borrowerId] = data
    return jsonify(data)

@app.route('/borrowers/<string:borrowerId>', methods=['DELETE'])
async def delete_borrower(borrowerId):
    if borrowerId not in borrowers:
        abort(404, description="Borrower not found")
    del borrowers[borrowerId]
    return '', 204

# Transactions endpoints
@app.route('/transactions', methods=['GET'])
async def get_transactions():
    return jsonify(list(transactions.values()))

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

if __name__ == '__main__':
    app.run()
