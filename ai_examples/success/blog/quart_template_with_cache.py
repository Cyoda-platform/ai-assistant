# blog_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
posts = {}
comments = {}  # key: postId, value: list of comments
post_id_counter = 1
comment_id_counter = 1

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
    comments[new_id] = []  # initialize comments list for this post
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

if __name__ == '__main__':
    app.run()
