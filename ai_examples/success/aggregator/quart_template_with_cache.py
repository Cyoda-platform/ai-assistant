# news_aggregator_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
articles = {}
sources = {}
topics = {}

article_id_counter = 1
source_id_counter = 1
topic_id_counter = 1

# Articles endpoints
@app.route('/articles', methods=['GET'])
async def get_articles():
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
    new_id = str(article_id_counter)
    article_id_counter += 1
    data['id'] = new_id
    articles[new_id] = data
    return jsonify(data), 201

@app.route('/articles/<string:articleId>', methods=['PUT'])
async def update_article(articleId):
    if articleId not in articles:
        abort(404, description="Article not found")
    data = await request.get_json()
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
    return jsonify(list(sources.values()))

@app.route('/sources', methods=['POST'])
async def create_source():
    global source_id_counter
    data = await request.get_json()
    new_id = str(source_id_counter)
    source_id_counter += 1
    data['id'] = new_id
    sources[new_id] = data
    return jsonify(data), 201

# Topics endpoints
@app.route('/topics', methods=['GET'])
async def get_topics():
    return jsonify(list(topics.values()))

@app.route('/topics', methods=['POST'])
async def create_topic():
    global topic_id_counter
    data = await request.get_json()
    new_id = str(topic_id_counter)
    topic_id_counter += 1
    data['id'] = new_id
    topics[new_id] = data
    return jsonify(data), 201

if __name__ == '__main__':
    app.run()
