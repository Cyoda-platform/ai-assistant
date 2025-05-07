# social_media_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
users = {}
posts = {}
comments = {}  # key: postId, value: list of comments
likes = {}     # key: postId, value: set of userIds

user_id_counter = 1
post_id_counter = 1
comment_id_counter = 1

# Users endpoints
@app.route('/users', methods=['GET'])
async def get_users():
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
    new_id = str(user_id_counter)
    user_id_counter += 1
    data['id'] = new_id
    users[new_id] = data
    return jsonify(data), 201

@app.route('/users/<string:userId>', methods=['PUT'])
async def update_user(userId):
    if userId not in users:
        abort(404, description="User not found")
    data = await request.get_json()
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
    new_id = str(post_id_counter)
    post_id_counter += 1
    data['id'] = new_id
    posts[new_id] = data
    comments[new_id] = []  # initialize comments list
    likes[new_id] = set()  # initialize likes set
    return jsonify(data), 201

@app.route('/posts/<string:postId>', methods=['PUT'])
async def update_post(postId):
    if postId not in posts:
        abort(404, description="Post not found")
    data = await request.get_json()
    data['id'] = postId
    posts[postId] = data
    return jsonify(data)

@app.route('/posts/<string:postId>', methods=['DELETE'])
async def delete_post(postId):
    if postId not in posts:
        abort(404, description="Post not found")
    del posts[postId]
    if postId in comments:
        del comments[postId]
    if postId in likes:
        del likes[postId]
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
    new_id = str(comment_id_counter)
    comment_id_counter += 1
    data['id'] = new_id
    data['postId'] = postId
    comments[postId].append(data)
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
