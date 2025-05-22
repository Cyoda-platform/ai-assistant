# news_aggregator_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Articles endpoints
@app.route('/articles', methods=['GET'])
async def get_articles():
    return jsonify([])

@app.route('/articles/<string:articleId>', methods=['GET'])
async def get_article(articleId):
    return jsonify({"id": articleId, "title": "News Article Title"})

# Sources endpoints
@app.route('/sources', methods=['GET'])
async def get_sources():
    return jsonify([])

# Topics endpoints
@app.route('/topics', methods=['GET'])
async def get_topics():
    return jsonify([])

if __name__ == '__main__':
    app.run()
