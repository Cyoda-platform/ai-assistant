from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
articles = {}
sources = {}
topics = {}

article_id_counter = 1
source_id_counter = 1
topic_id_counter = 1

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

def validate_article(data):
    if 'title' not in data or 'content' not in data:
        abort(400, description="Article must have 'title' and 'content'")
    return data

def validate_source(data):
    if 'name' not in data:
        abort(400, description="Source must have 'name'")
    return data

def validate_topic(data):
    if 'name' not in data:
        abort(400, description="Topic must have 'name'")
    return data

# Articles endpoints
@app.route('/articles', methods=['GET'])
async def get_articles():
    await call_mock_service("GET", "posts")
    return jsonify(list(articles.values()))

@app.route('/articles/<string:articleId>', methods=['GET'])
async def get_article(articleId):
    article = articles.get(articleId)
    if not article:
        abort(404, description="Article not found")
    return jsonify(article)

@app.route('/articles', methods=['POST'])
async def create_article():
    global article_id_counter
    data = await request.get_json()
    validate_article(data)
    new_id = str(article_id_counter)
    article_id_counter += 1
    data['id'] = new_id
    articles[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/articles/<string:articleId>', methods=['PUT'])
async def update_article(articleId):
    if articleId not in articles:
        abort(404, description="Article not found")
    data = await request.get_json()
    validate_article(data)
    data['id'] = articleId
    articles[articleId] = data
    return jsonify(data)

@app.route('/articles/<string:articleId>', methods=['DELETE'])
async def delete_article(articleId):
    if articleId not in articles:
        abort(404, description="Article not found")
    del articles[articleId]
    return '', 204

# Sources endpoints
@app.route('/sources', methods=['GET'])
async def get_sources():
    await call_mock_service("GET", "users")
    return jsonify(list(sources.values()))

@app.route('/sources', methods=['POST'])
async def create_source():
    global source_id_counter
    data = await request.get_json()
    validate_source(data)
    new_id = str(source_id_counter)
    source_id_counter += 1
    data['id'] = new_id
    sources[new_id] = data
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

# Topics endpoints
@app.route('/topics', methods=['GET'])
async def get_topics():
    await call_mock_service("GET", "posts")
    return jsonify(list(topics.values()))

@app.route('/topics', methods=['POST'])
async def create_topic():
    global topic_id_counter
    data = await request.get_json()
    validate_topic(data)
    new_id = str(topic_id_counter)
    topic_id_counter += 1
    data['id'] = new_id
    topics[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

if __name__ == '__main__':
    app.run()
