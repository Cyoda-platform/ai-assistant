# education_api.py
from quart import Quart, jsonify, request

app = Quart(__name__)

# Courses endpoints
@app.route('/courses', methods=['GET'])
async def get_courses():
    return jsonify([])

@app.route('/courses/<string:courseId>', methods=['GET'])
async def get_course(courseId):
    return jsonify({"id": courseId, "title": "Introduction to Programming"})

@app.route('/courses', methods=['POST'])
async def create_course():
    data = await request.get_json()
    return jsonify(data), 201

@app.route('/courses/<string:courseId>', methods=['PUT'])
async def update_course(courseId):
    data = await request.get_json()
    return jsonify({"id": courseId, **data})

@app.route('/courses/<string:courseId>', methods=['DELETE'])
async def delete_course(courseId):
    return '', 204

# Enrollments endpoints
@app.route('/enrollments', methods=['GET'])
async def get_enrollments():
    return jsonify([])

@app.route('/courses/<string:courseId>/enrollments', methods=['POST'])
async def create_enrollment(courseId):
    data = await request.get_json()
    return jsonify({"courseId": courseId, **data}), 201

@app.route('/enrollments/<string:enrollmentId>', methods=['DELETE'])
async def delete_enrollment(enrollmentId):
    return '', 204

if __name__ == '__main__':
    app.run()
