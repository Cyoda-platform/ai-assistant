from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
users = {}
posts = {}
comments = {}  # key: postId, value: list of comments
likes = {}     # key: postId, value: set of userIds

user_id_counter = 1
post_id_counter = 1
comment_id_counter = 1

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

def validate_user(data):
    if 'username' not in data or 'email' not in data:
        abort(400, description="User must have 'username' and 'email'")
    return data

def validate_post(data):
    if 'content' not in data:
        abort(400, description="Post must have 'content'")
    return data

def validate_comment(data):
    if 'userId' not in data or 'content' not in data:
        abort(400, description="Comment must have 'userId' and 'content'")
    return data

# Users endpoints
@app.route('/users', methods=['GET'])
async def get_users():
    await call_mock_service("GET", "users")
    return jsonify(list(users.values()))

@app.route('/users/<string:userId>', methods=['GET'])
async def get_user(userId):
    user = users.get(userId)
    if not user:
        abort(404, description="User not found")
    return jsonify(user)

@app.route('/users', methods=['POST'])
async def create_user():
    global user_id_counter
    data = await request.get_json()
    validate_user(data)
    new_id = str(user_id_counter)
    user_id_counter += 1
    data['id'] = new_id
    users[new_id] = data
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

@app.route('/users/<string:userId>', methods=['PUT'])
async def update_user(userId):
    if userId not in users:
        abort(404, description="User not found")
    data = await request.get_json()
    validate_user(data)
    data['id'] = userId
    users[userId] = data
    return jsonify(data)

@app.route('/users/<string:userId>', methods=['DELETE'])
async def delete_user(userId):
    if userId not in users:
        abort(404, description="User not found")
    del users[userId]
    return '', 204

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
    comments[new_id] = []
    likes[new_id] = set()
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
    likes.pop(postId, None)
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

# Likes endpoints
@app.route('/posts/<string:postId>/likes', methods=['POST'])
async def like_post(postId):
    if postId not in posts:
        abort(404, description="Post not found")
    data = await request.get_json()
    userId = data.get('userId')
    if not userId or userId not in users:
        abort(400, description="Invalid userId")
    likes[postId].add(userId)
    return jsonify({"postId": postId, "likes": list(likes[postId])}), 201

@app.route('/posts/<string:postId>/likes/<string:userId>', methods=['DELETE'])
async def unlike_post(postId, userId):
    if postId not in posts or userId not in users:
        abort(404, description="Post or User not found")
    likes[postId].discard(userId)
    return '', 204

if __name__ == '__main__':
    app.run()
