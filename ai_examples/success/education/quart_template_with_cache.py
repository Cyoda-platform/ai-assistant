# education_api.py
from quart import Quart, jsonify, request, abort

app = Quart(__name__)

# In-memory "database"
courses = {}
enrollments = {}

course_id_counter = 1
enrollment_id_counter = 1

# Courses endpoints
@app.route('/courses', methods=['GET'])
async def get_courses():
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
    new_id = str(course_id_counter)
    course_id_counter += 1
    data['id'] = new_id
    courses[new_id] = data
    return jsonify(data), 201

@app.route('/courses/<string:courseId>', methods=['PUT'])
async def update_course(courseId):
    if courseId not in courses:
        abort(404, description="Course not found")
    data = await request.get_json()
    data['id'] = courseId
    courses[courseId] = data
    return jsonify(data)

@app.route('/courses/<string:courseId>', methods=['DELETE'])
async def delete_course(courseId):
    if courseId not in courses:
        abort(404, description="Course not found")
    del courses[courseId]
    # Remove related enrollments
    to_delete = [eid for eid, enroll in enrollments.items() if enroll.get('courseId') == courseId]
    for eid in to_delete:
        del enrollments[eid]
    return '', 204

# Enrollments endpoints
@app.route('/enrollments', methods=['GET'])
async def get_enrollments():
    return jsonify(list(enrollments.values()))

@app.route('/courses/<string:courseId>/enrollments', methods=['POST'])
async def create_enrollment(courseId):
    if courseId not in courses:
        abort(404, description="Course not found")
    global enrollment_id_counter
    data = await request.get_json()
    new_id = str(enrollment_id_counter)
    enrollment_id_counter += 1
    data['id'] = new_id
    data['courseId'] = courseId
    enrollments[new_id] = data
    return jsonify(data), 201

@app.route('/enrollments/<string:enrollmentId>', methods=['DELETE'])
async def delete_enrollment(enrollmentId):
    if enrollmentId not in enrollments:
        abort(404, description="Enrollment not found")
    del enrollments[enrollmentId]
    return '', 204

if __name__ == '__main__':
    app.run()
