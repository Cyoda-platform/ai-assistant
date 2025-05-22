from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
contacts = {}
leads = {}
opportunities = {}

contact_id_counter = 1
lead_id_counter = 1
opportunity_id_counter = 1

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

def validate_contact(data):
    if 'firstName' not in data or 'email' not in data:
        abort(400, description="Contact must have 'firstName' and 'email'")
    return data

def validate_lead(data):
    if 'name' not in data:
        abort(400, description="Lead must have 'name'")
    return data

def validate_opportunity(data):
    if 'description' not in data:
        abort(400, description="Opportunity must have 'description'")
    return data

# Contacts endpoints
@app.route('/contacts', methods=['GET'])
async def get_contacts():
    await call_mock_service("GET", "users")
    return jsonify(list(contacts.values()))

@app.route('/contacts/<string:contactId>', methods=['GET'])
async def get_contact(contactId):
    contact = contacts.get(contactId)
    if not contact:
        abort(404, description="Contact not found")
    return jsonify(contact)

@app.route('/contacts', methods=['POST'])
async def create_contact():
    global contact_id_counter
    data = await request.get_json()
    validate_contact(data)
    new_id = str(contact_id_counter)
    contact_id_counter += 1
    data['id'] = new_id
    contacts[new_id] = data
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

@app.route('/contacts/<string:contactId>', methods=['PUT'])
async def update_contact(contactId):
    if contactId not in contacts:
        abort(404, description="Contact not found")
    data = await request.get_json()
    validate_contact(data)
    data['id'] = contactId
    contacts[contactId] = data
    return jsonify(data)

@app.route('/contacts/<string:contactId>', methods=['DELETE'])
async def delete_contact(contactId):
    if contactId not in contacts:
        abort(404, description="Contact not found")
    del contacts[contactId]
    return '', 204

# Leads endpoints
@app.route('/leads', methods=['GET'])
async def get_leads():
    await call_mock_service("GET", "posts")
    return jsonify(list(leads.values()))

@app.route('/leads/<string:leadId>', methods=['GET'])
async def get_lead(leadId):
    lead = leads.get(leadId)
    if not lead:
        abort(404, description="Lead not found")
    return jsonify(lead)

@app.route('/leads', methods=['POST'])
async def create_lead():
    global lead_id_counter
    data = await request.get_json()
    validate_lead(data)
    new_id = str(lead_id_counter)
    lead_id_counter += 1
    data['id'] = new_id
    leads[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/leads/<string:leadId>', methods=['PUT'])
async def update_lead(leadId):
    if leadId not in leads:
        abort(404, description="Lead not found")
    data = await request.get_json()
    validate_lead(data)
    data['id'] = leadId
    leads[leadId] = data
    return jsonify(data)

@app.route('/leads/<string:leadId>', methods=['DELETE'])
async def delete_lead(leadId):
    if leadId not in leads:
        abort(404, description="Lead not found")
    del leads[leadId]
    return '', 204

# Opportunities endpoints
@app.route('/opportunities', methods=['GET'])
async def get_opportunities():
    await call_mock_service("GET", "posts")
    return jsonify(list(opportunities.values()))

@app.route('/opportunities/<string:oppId>', methods=['GET'])
async def get_opportunity(oppId):
    opp = opportunities.get(oppId)
    if not opp:
        abort(404, description="Opportunity not found")
    return jsonify(opp)

@app.route('/opportunities', methods=['POST'])
async def create_opportunity():
    global opportunity_id_counter
    data = await request.get_json()
    validate_opportunity(data)
    new_id = str(opportunity_id_counter)
    opportunity_id_counter += 1
    data['id'] = new_id
    opportunities[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/opportunities/<string:oppId>', methods=['PUT'])
async def update_opportunity(oppId):
    if oppId not in opportunities:
        abort(404, description="Opportunity not found")
    data = await request.get_json()
    validate_opportunity(data)
    data['id'] = oppId
    opportunities[oppId] = data
    return jsonify(data)

if __name__ == '__main__':
    app.run()
