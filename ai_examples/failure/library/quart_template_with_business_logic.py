from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
books = {}
authors = {}
borrowers = {}
transactions = {}

book_id_counter = 1
author_id_counter = 1
borrower_id_counter = 1
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

# Validation functions
def validate_book(data):
    if 'title' not in data or 'authorId' not in data:
        abort(400, description="Book must have 'title' and 'authorId'")
    return data

def validate_author(data):
    if 'name' not in data:
        abort(400, description="Author must have a 'name'")
    return data

def validate_borrower(data):
    if 'name' not in data or 'email' not in data:
        abort(400, description="Borrower must have 'name' and 'email'")
    return data

def validate_transaction(data):
    if 'bookId' not in data or 'borrowerId' not in data:
        abort(400, description="Transaction must have 'bookId' and 'borrowerId'")
    return data

# Books endpoints
@app.route('/books', methods=['GET'])
async def get_books():
    await call_mock_service("GET", "posts")
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
    validate_book(data)
    new_id = str(book_id_counter)
    book_id_counter += 1
    data['id'] = new_id
    books[new_id] = data
    # Simulate external indexing
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/books/<string:bookId>', methods=['PUT'])
async def update_book(bookId):
    if bookId not in books:
        abort(404, description="Book not found")
    data = await request.get_json()
    validate_book(data)
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
    await call_mock_service("GET", "users")
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
    validate_author(data)
    new_id = str(author_id_counter)
    author_id_counter += 1
    data['id'] = new_id
    authors[new_id] = data
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

@app.route('/authors/<string:authorId>', methods=['PUT'])
async def update_author(authorId):
    if authorId not in authors:
        abort(404, description="Author not found")
    data = await request.get_json()
    validate_author(data)
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
    await call_mock_service("GET", "users")
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
    validate_borrower(data)
    new_id = str(borrower_id_counter)
    borrower_id_counter += 1
    data['id'] = new_id
    borrowers[new_id] = data
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

@app.route('/borrowers/<string:borrowerId>', methods=['PUT'])
async def update_borrower(borrowerId):
    if borrowerId not in borrowers:
        abort(404, description="Borrower not found")
    data = await request.get_json()
    validate_borrower(data)
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
    await call_mock_service("GET", "posts")
    return jsonify(list(transactions.values()))

@app.route('/transactions', methods=['POST'])
async def create_transaction():
    global transaction_id_counter
    data = await request.get_json()
    validate_transaction(data)
    new_id = str(transaction_id_counter)
    transaction_id_counter += 1
    data['id'] = new_id
    transactions[new_id] = data
    # Simulate external transaction processing
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

if __name__ == '__main__':
    app.run()
