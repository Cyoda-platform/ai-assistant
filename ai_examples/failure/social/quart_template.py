# social_media_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Users endpoints
@app.route('/users', methods=['GET'])
async def get_users():
    return jsonify([])

@app.route('/users/<string:userId>', methods=['GET'])
async def get_user(userId):
    return jsonify({"id": userId, "username": "newuser"})

@app.route('/users', methods=['POST'])
async def create_user():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/users/<string:userId>', methods=['PUT'])
async def update_user(userId):
    data = await request.get_json()
    return jsonify({"id": userId, **data})

@app.route('/users/<string:userId>', methods=['DELETE'])
async def delete_user(userId):
    return '', 204

# Posts endpoints
@app.route('/posts', methods=['GET'])
async def get_posts():
    return jsonify([])

@app.route('/posts/<string:postId>', methods=['GET'])
async def get_post(postId):
    return jsonify({"id": postId, "content": "Excited to share my latest adventure!"})

@app.route('/posts', methods=['POST'])
async def create_post():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/posts/<string:postId>', methods=['PUT'])
async def update_post(postId):
    data = await request.get_json()
    return jsonify({"id": postId, **data})

@app.route('/posts/<string:postId>', methods=['DELETE'])
async def delete_post(postId):
    return '', 204

# Comments endpoints
@app.route('/posts/<string:postId>/comments', methods=['GET'])
async def get_comments(postId):
    return jsonify([])

@app.route('/posts/<string:postId>/comments', methods=['POST'])
async def create_comment(postId):
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/posts/<string:postId>/comments/<string:commentId>', methods=['DELETE'])
async def delete_comment(postId, commentId):
    return '', 204

# Likes endpoints
@app.route('/posts/<string:postId>/likes', methods=['POST'])
async def like_post(postId):
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/posts/<string:postId>/likes/<string:userId>', methods=['DELETE'])
async def unlike_post(postId, userId):
    return '', 204

if __name__ == '__main__':
    app.run()
