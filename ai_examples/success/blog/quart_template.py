# blog_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Posts endpoints
@app.route('/posts', methods=['GET'])
async def get_posts():
    return jsonify([{"id": "1", "title": "Understanding REST APIs"}])

@app.route('/posts/<string:postId>', methods=['GET'])
async def get_post(postId):
    return jsonify({"id": postId, "title": "Understanding REST APIs", "content": "Lorem ipsum..."})

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

if __name__ == '__main__':
    app.run()
