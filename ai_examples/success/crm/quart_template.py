# crm_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Contacts endpoints
@app.route('/contacts', methods=['GET'])
async def get_contacts():
    return jsonify([])

@app.route('/contacts/<string:contactId>', methods=['GET'])
async def get_contact(contactId):
    return jsonify({"id": contactId, "firstName": "John", "lastName": "Doe"})

@app.route('/contacts', methods=['POST'])
async def create_contact():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/contacts/<string:contactId>', methods=['PUT'])
async def update_contact(contactId):
    data = await request.get_json()
    return jsonify({"id": contactId, **data})

@app.route('/contacts/<string:contactId>', methods=['DELETE'])
async def delete_contact(contactId):
    return '', 204

# Leads endpoints
@app.route('/leads', methods=['GET'])
async def get_leads():
    return jsonify([])

@app.route('/leads/<string:leadId>', methods=['GET'])
async def get_lead(leadId):
    return jsonify({"id": leadId})

@app.route('/leads', methods=['POST'])
async def create_lead():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/leads/<string:leadId>', methods=['PUT'])
async def update_lead(leadId):
    data = await request.get_json()
    return jsonify({"id": leadId, **data})

@app.route('/leads/<string:leadId>', methods=['DELETE'])
async def delete_lead(leadId):
    return '', 204

# Opportunities endpoints
@app.route('/opportunities', methods=['GET'])
async def get_opportunities():
    return jsonify([])

@app.route('/opportunities/<string:oppId>', methods=['GET'])
async def get_opportunity(oppId):
    return jsonify({"id": oppId})

@app.route('/opportunities', methods=['POST'])
async def create_opportunity():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/opportunities/<string:oppId>', methods=['PUT'])
async def update_opportunity(oppId):
    data = await request.get_json()
    return jsonify({"id": oppId, **data})

if __name__ == '__main__':
    app.run()
