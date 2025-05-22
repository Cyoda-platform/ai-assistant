from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
posts = {}
comments = {}  # key: postId, value: list of comments
post_id_counter = 1
comment_id_counter = 1

# Helper function for external API calls
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
def validate_post(data):
    if 'title' not in data or 'content' not in data:
        abort(400, description="Post must have 'title' and 'content'")
    return data

def validate_comment(data):
    if 'author' not in data or 'content' not in data:
        abort(400, description="Comment must have 'author' and 'content'")
    return data

# Posts endpoints
@app.route('/posts', methods=['GET'])
async def get_posts():
    await call_mock_service("GET", "posts")
    return jsonify(list(posts.values()))

@app.route('/posts/<string:postId>', methods=['GET'])
async def get_post(postId):
    post = posts.get(postId)
    if not post:
        abort(404, description="Post not found")
    return jsonify(post)

@app.route('/posts', methods=['POST'])
async def create_post():
    global post_id_counter
    data = await request.get_json()
    validate_post(data)
    new_id = str(post_id_counter)
    post_id_counter += 1
    data['id'] = new_id
    posts[new_id] = data
    comments[new_id] = []  # initialize empty comments list
    # Simulate indexing the post externally
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/posts/<string:postId>', methods=['PUT'])
async def update_post(postId):
    if postId not in posts:
        abort(404, description="Post not found")
    data = await request.get_json()
    validate_post(data)
    data['id'] = postId
    posts[postId] = data
    return jsonify(data)

@app.route('/posts/<string:postId>', methods=['DELETE'])
async def delete_post(postId):
    if postId not in posts:
        abort(404, description="Post not found")
    del posts[postId]
    comments.pop(postId, None)
    return '', 204

# Comments endpoints
@app.route('/posts/<string:postId>/comments', methods=['GET'])
async def get_comments(postId):
    if postId not in posts:
        abort(404, description="Post not found")
    return jsonify(comments.get(postId, []))

@app.route('/posts/<string:postId>/comments', methods=['POST'])
async def create_comment(postId):
    global comment_id_counter
    if postId not in posts:
        abort(404, description="Post not found")
    data = await request.get_json()
    validate_comment(data)
    new_id = str(comment_id_counter)
    comment_id_counter += 1
    data['id'] = new_id
    data['postId'] = postId
    comments[postId].append(data)
    # Simulate notifying the post author via an external service
    await call_mock_service("POST", "comments", data)
    return jsonify(data), 201

@app.route('/posts/<string:postId>/comments/<string:commentId>', methods=['DELETE'])
async def delete_comment(postId, commentId):
    if postId not in posts:
        abort(404, description="Post not found")
    post_comments = comments.get(postId, [])
    for idx, comment in enumerate(post_comments):
        if comment['id'] == commentId:
            del post_comments[idx]
            return '', 204
    abort(404, description="Comment not found")

if __name__ == '__main__':
    app.run()
