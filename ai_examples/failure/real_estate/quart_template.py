# real_estate_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Properties endpoints
@app.route('/properties', methods=['GET'])
async def get_properties():
    return jsonify([])

@app.route('/properties/<string:propertyId>', methods=['GET'])
async def get_property(propertyId):
    return jsonify({"id": propertyId, "title": "Modern Family Home"})

@app.route('/properties', methods=['POST'])
async def create_property():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/properties/<string:propertyId>', methods=['PUT'])
async def update_property(propertyId):
    data = await request.get_json()
    return jsonify({"id": propertyId, **data})

@app.route('/properties/<string:propertyId>', methods=['DELETE'])
async def delete_property(propertyId):
    return '', 204

# Agents endpoints
@app.route('/agents', methods=['GET'])
async def get_agents():
    return jsonify([])

@app.route('/agents/<string:agentId>', methods=['GET'])
async def get_agent(agentId):
    return jsonify({"id": agentId, "name": "Agent Smith"})

if __name__ == '__main__':
    app.run()
