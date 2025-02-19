from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
courses = {}
enrollments = {}

course_id_counter = 1
enrollment_id_counter = 1

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

def validate_course(data):
    if 'title' not in data or 'description' not in data:
        abort(400, description="Course must have 'title' and 'description'")
    return data

def validate_enrollment(data):
    if 'studentId' not in data or 'enrollmentDate' not in data:
        abort(400, description="Enrollment must have 'studentId' and 'enrollmentDate'")
    return data

# Courses endpoints
@app.route('/courses', methods=['GET'])
async def get_courses():
    await call_mock_service("GET", "posts")
    return jsonify(list(courses.values()))

@app.route('/courses/<string:courseId>', methods=['GET'])
async def get_course(courseId):
    course = courses.get(courseId)
    if not course:
        abort(404, description="Course not found")
    return jsonify(course)

@app.route('/courses', methods=['POST'])
async def create_course():
    global course_id_counter
    data = await request.get_json()
    validate_course(data)
    new_id = str(course_id_counter)
    course_id_counter += 1
    data['id'] = new_id
    courses[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/courses/<string:courseId>', methods=['PUT'])
async def update_course(courseId):
    if courseId not in courses:
        abort(404, description="Course not found")
    data = await request.get_json()
    validate_course(data)
    data['id'] = courseId
    courses[courseId] = data
    return jsonify(data)

@app.route('/courses/<string:courseId>', methods=['DELETE'])
async def delete_course(courseId):
    if courseId not in courses:
        abort(404, description="Course not found")
    del courses[courseId]
    # Also remove related enrollments
    to_delete = [eid for eid, enroll in enrollments.items() if enroll.get('courseId') == courseId]
    for eid in to_delete:
        del enrollments[eid]
    return '', 204

# Enrollments endpoints
@app.route('/enrollments', methods=['GET'])
async def get_enrollments():
    await call_mock_service("GET", "posts")
    return jsonify(list(enrollments.values()))

@app.route('/courses/<string:courseId>/enrollments', methods=['POST'])
async def create_enrollment(courseId):
    if courseId not in courses:
        abort(404, description="Course not found")
    global enrollment_id_counter
    data = await request.get_json()
    validate_enrollment(data)
    new_id = str(enrollment_id_counter)
    enrollment_id_counter += 1
    data['id'] = new_id
    data['courseId'] = courseId
    enrollments[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/enrollments/<string:enrollmentId>', methods=['DELETE'])
async def delete_enrollment(enrollmentId):
    if enrollmentId not in enrollments:
        abort(404, description="Enrollment not found")
    del enrollments[enrollmentId]
    return '', 204

if __name__ == '__main__':
    app.run()
