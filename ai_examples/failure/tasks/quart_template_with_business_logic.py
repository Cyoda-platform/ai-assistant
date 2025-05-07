from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
projects = {}
tasks = {}

project_id_counter = 1
task_id_counter = 1

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

def validate_project(data):
    if 'name' not in data or 'description' not in data:
        abort(400, description="Project must have 'name' and 'description'")
    return data

def validate_task(data):
    if 'title' not in data:
        abort(400, description="Task must have a 'title'")
    return data

# Projects endpoints
@app.route('/projects', methods=['GET'])
async def get_projects():
    await call_mock_service("GET", "posts")
    return jsonify(list(projects.values()))

@app.route('/projects/<string:projectId>', methods=['GET'])
async def get_project(projectId):
    project = projects.get(projectId)
    if not project:
        abort(404, description="Project not found")
    return jsonify(project)

@app.route('/projects', methods=['POST'])
async def create_project():
    global project_id_counter
    data = await request.get_json()
    validate_project(data)
    new_id = str(project_id_counter)
    project_id_counter += 1
    data['id'] = new_id
    projects[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/projects/<string:projectId>', methods=['PUT'])
async def update_project(projectId):
    if projectId not in projects:
        abort(404, description="Project not found")
    data = await request.get_json()
    validate_project(data)
    data['id'] = projectId
    projects[projectId] = data
    return jsonify(data)

@app.route('/projects/<string:projectId>', methods=['DELETE'])
async def delete_project(projectId):
    if projectId not in projects:
        abort(404, description="Project not found")
    del projects[projectId]
    # Also remove tasks associated with this project
    to_delete = [tid for tid, task in tasks.items() if task.get('projectId') == projectId]
    for tid in to_delete:
        del tasks[tid]
    return '', 204

# Tasks endpoints
@app.route('/projects/<string:projectId>/tasks', methods=['GET'])
async def get_tasks_for_project(projectId):
    if projectId not in projects:
        abort(404, description="Project not found")
    project_tasks = [task for task in tasks.values() if task.get('projectId') == projectId]
    return jsonify(project_tasks)

@app.route('/tasks/<string:taskId>', methods=['GET'])
async def get_task(taskId):
    task = tasks.get(taskId)
    if not task:
        abort(404, description="Task not found")
    return jsonify(task)

@app.route('/projects/<string:projectId>/tasks', methods=['POST'])
async def create_task(projectId):
    if projectId not in projects:
        abort(404, description="Project not found")
    global task_id_counter
    data = await request.get_json()
    validate_task(data)
    new_id = str(task_id_counter)
    task_id_counter += 1
    data['id'] = new_id
    data['projectId'] = projectId
    tasks[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/tasks/<string:taskId>', methods=['PUT'])
async def update_task(taskId):
    if taskId not in tasks:
        abort(404, description="Task not found")
    data = await request.get_json()
    validate_task(data)
    data['id'] = taskId
    tasks[taskId] = data
    return jsonify(data)

@app.route('/tasks/<string:taskId>', methods=['PATCH'])
async def patch_task(taskId):
    if taskId not in tasks:
        abort(404, description="Task not found")
    data = await request.get_json()
    tasks[taskId].update(data)
    return jsonify(tasks[taskId])

@app.route('/tasks/<string:taskId>', methods=['DELETE'])
async def delete_task(taskId):
    if taskId not in tasks:
        abort(404, description="Task not found")
    del tasks[taskId]
    return '', 204

if __name__ == '__main__':
    app.run()
