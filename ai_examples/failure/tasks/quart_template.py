# task_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Projects endpoints
@app.route('/projects', methods=['GET'])
async def get_projects():
    return jsonify([])

@app.route('/projects/<string:projectId>', methods=['GET'])
async def get_project(projectId):
    return jsonify({"id": projectId, "name": "Website Redesign"})

@app.route('/projects', methods=['POST'])
async def create_project():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/projects/<string:projectId>', methods=['PUT'])
async def update_project(projectId):
    data = await request.get_json()
    return jsonify({"id": projectId, **data})

@app.route('/projects/<string:projectId>', methods=['DELETE'])
async def delete_project(projectId):
    return '', 204

# Tasks endpoints
@app.route('/projects/<string:projectId>/tasks', methods=['GET'])
async def get_tasks(projectId):
    return jsonify([])

@app.route('/tasks/<string:taskId>', methods=['GET'])
async def get_task(taskId):
    return jsonify({"id": taskId, "title": "Design Homepage"})

@app.route('/projects/<string:projectId>/tasks', methods=['POST'])
async def create_task(projectId):
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/tasks/<string:taskId>', methods=['PUT'])
async def update_task(taskId):
    data = await request.get_json()
    return jsonify({"id": taskId, **data})

@app.route('/tasks/<string:taskId>', methods=['PATCH'])
async def patch_task(taskId):
    data = await request.get_json()
    return jsonify({"id": taskId, **data})

@app.route('/tasks/<string:taskId>', methods=['DELETE'])
async def delete_task(taskId):
    return '', 204

if __name__ == '__main__':
    app.run()
