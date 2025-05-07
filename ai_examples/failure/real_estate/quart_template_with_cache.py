# real_estate_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
properties = {}
agents = {}

property_id_counter = 1
agent_id_counter = 1

# Properties endpoints
@app.route('/properties', methods=['GET'])
async def get_properties():
    return jsonify(list(properties.values()))

@app.route('/properties/<string:propertyId>', methods=['GET'])
async def get_property(propertyId):
    prop = properties.get(propertyId)
    if not prop:
        abort(404, description="Property not found")
    return jsonify(prop)

@app.route('/properties', methods=['POST'])
async def create_property():
    global property_id_counter
    data = await request.get_json()
    new_id = str(property_id_counter)
    property_id_counter += 1
    data['id'] = new_id
    properties[new_id] = data
    return jsonify(data), 201

@app.route('/properties/<string:propertyId>', methods=['PUT'])
async def update_property(propertyId):
    if propertyId not in properties:
        abort(404, description="Property not found")
    data = await request.get_json()
    data['id'] = propertyId
    properties[propertyId] = data
    return jsonify(data)

@app.route('/properties/<string:propertyId>', methods=['DELETE'])
async def delete_property(propertyId):
    if propertyId not in properties:
        abort(404, description="Property not found")
    del properties[propertyId]
    return '', 204

# Agents endpoints
@app.route('/agents', methods=['GET'])
async def get_agents():
    return jsonify(list(agents.values()))

@app.route('/agents/<string:agentId>', methods=['GET'])
async def get_agent(agentId):
    agent = agents.get(agentId)
    if not agent:
        abort(404, description="Agent not found")
    return jsonify(agent)

@app.route('/agents', methods=['POST'])
async def create_agent():
    global agent_id_counter
    data = await request.get_json()
    new_id = str(agent_id_counter)
    agent_id_counter += 1
    data['id'] = new_id
    agents[new_id] = data
    return jsonify(data), 201

@app.route('/agents/<string:agentId>', methods=['PUT'])
async def update_agent(agentId):
    if agentId not in agents:
        abort(404, description="Agent not found")
    data = await request.get_json()
    data['id'] = agentId
    agents[agentId] = data
    return jsonify(data)

@app.route('/agents/<string:agentId>', methods=['DELETE'])
async def delete_agent(agentId):
    if agentId not in agents:
        abort(404, description="Agent not found")
    del agents[agentId]
    return '', 204

if __name__ == '__main__':
    app.run()
