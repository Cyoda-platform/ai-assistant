import json
import unittest

from entity.chat.workflow.gen_and_validation.entities_design_generator import extract_endpoints, generate_spec

WORK_DIR="/home/kseniia/PycharmProjects/ai_assistant"

def read_file(file_path):
    """
    Reads the content of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

class TestFunctions(unittest.TestCase):

    def test_question_enqueues_aggregator(self):
        content = read_file(f"{WORK_DIR}/ai_examples/failure/aggregator/quart_template_with_cache.py")

        endpoints = extract_endpoints(content)
        spec = generate_spec(endpoints)
        result = json.dumps(spec, indent=4)
        print(result)
        #expected_result_json = ""
        #expected_result = json.dumps(expected_result_json, indent=4)
        #self.assertEqual(result, expected_result)




    def test_question_enqueues_event_posts(self):
        content = """
# This is a prototype implementation using Quart.
# The code includes endpoints for users, posts, and nested sub-resources like comments, images, and votes.
# 
# ```python
from quart import Quart, request, jsonify
from quart_schema import QuartSchema
import aiohttp

app = Quart(__name__)
QuartSchema(app)

# In-memory data storage for demonstration purposes
users = {}
posts = {}
comments = {}
images = {}
votes = {}

@app.route('/users/create', methods=['POST'])
async def create_user():
    data = await request.json
    username = data.get('username')
    password = data.get('password')
    users[username] = {'password': password}
    return jsonify({"message": "User created successfully."}), 201

@app.route('/users/login', methods=['POST'])
async def login_user():
    data = await request.json
    username = data.get('username')
    password = data.get('password')
    if username in users and users[username]['password'] == password:
        return jsonify({"token": "your_jwt_token"}), 200
    return jsonify({"message": "Invalid credentials."}), 401

@app.route('/posts', methods=['POST'])
async def create_post():
    data = await request.json
    post_id = str(len(posts) + 1)
    posts[post_id] = {
        "post_id": post_id,
        "title": data.get('title'),
        "topics": data.get('topics'),
        "body": data.get('body'),
        "upvotes": 0,
        "downvotes": 0
    }
    return jsonify({"post_id": post_id, "message": "Post created successfully."}), 201

@app.route('/posts', methods=['GET'])
async def get_posts():
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    return jsonify({"posts": list(posts.values())[offset:offset + limit]}), 200

@app.route('/posts/<post_id>', methods=['GET'])
async def get_post(post_id):
    post = posts.get(post_id)
    if post:
        return jsonify(post), 200
    return jsonify({"message": "Post not found."}), 404

@app.route('/posts/<post_id>', methods=['DELETE'])
async def delete_post(post_id):
    if post_id in posts:
        del posts[post_id]
        return jsonify({"message": "Post deleted successfully."}), 200
    return jsonify({"message": "Post not found."}), 404

@app.route('/posts/<post_id>/comments', methods=['POST'])
async def add_comment(post_id):
    data = await request.json
    comment_id = str(len(comments) + 1)
    comments[comment_id] = {
        "comment_id": comment_id,
        "body": data.get('body'),
        "post_id": post_id,
        "upvotes": 0,
        "downvotes": 0
    }
    return jsonify({"comment_id": comment_id, "message": "Comment added successfully."}), 201

@app.route('/posts/<post_id>/comments', methods=['GET'])
async def get_comments(post_id):
    post_comments = [comment for comment in comments.values() if comment['post_id'] == post_id]
    return jsonify({"comments": post_comments}), 200

@app.route('/posts/<post_id>/comments/<comment_id>', methods=['DELETE'])
async def delete_comment(post_id, comment_id):
    if comment_id in comments and comments[comment_id]['post_id'] == post_id:
        del comments[comment_id]
        return jsonify({"message": "Comment deleted successfully."}), 200
    return jsonify({"message": "Comment not found."}), 404

@app.route('/posts/<post_id>/images', methods=['POST'])
async def upload_image(post_id):
    image_id = str(len(images) + 1)
    images[image_id] = {"post_id": post_id, "image_data": "mock_image_data"}
    return jsonify({"image_id": image_id, "message": "Image uploaded successfully."}), 201

@app.route('/posts/<post_id>/images/<image_id>', methods=['GET'])
async def get_image(post_id, image_id):
    if image_id in images and images[image_id]['post_id'] == post_id:
        return jsonify(images[image_id]), 200
    return jsonify({"message": "Image not found."}), 404

@app.route('/posts/<post_id>/vote', methods=['POST'])
async def vote_post(post_id):
    data = await request.json
    vote = data.get('vote')
    if vote not in ['up', 'down']:
        return jsonify({"message": "Invalid vote."}), 400
    if vote == 'up':
        posts[post_id]['upvotes'] += 1
    else:
        posts[post_id]['downvotes'] += 1
    return jsonify({"message": "Vote recorded."}), 200

@app.route('/posts/<post_id>/comments/<comment_id>/vote', methods=['POST'])
async def vote_comment(post_id, comment_id):
    data = await request.json
    vote = data.get('vote')
    if vote not in ['up', 'down']:
        return jsonify({"message": "Invalid vote."}), 400
    if vote == 'up':
        comments[comment_id]['upvotes'] += 1
    else:
        comments[comment_id]['downvotes'] += 1
    return jsonify({"message": "Vote recorded."}), 200

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
# ```
    """

        endpoints = extract_endpoints(content)
        spec = generate_spec(endpoints)
        result = json.dumps(spec, indent=4)
        expected_result_json = {
    "primary_entities": [
        {
            "entity_name": "user",
            "endpoints": {
                "POST": [
                    {
                        "endpoint": "/users/create",
                        "description": "Create a new user.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    username = data.get('username')\n    password = data.get('password')\n    users[username] = {'password': password}\n    return jsonify({\"message\": \"User created successfully.\"}), 201\n",
                        "action": "create_user",
                        "suggested_workflow": [{
                            "start_state": "user_not_created",
                            "end_state": "user_created",
                            "action": "create_user",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    username = data.get('username')\n    password = data.get('password')\n    users[username] = {'password': password}\n    return jsonify({\"message\": \"User created successfully.\"}), 201\n",
                            "description": "Create a new user.",
                            "related_secondary_entities": []
                        }]
                    },
                    {
                        "endpoint": "/users/login",
                        "description": "Create a new user.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    username = data.get('username')\n    password = data.get('password')\n    if username in users and users[username]['password'] == password:\n        return jsonify({\"token\": \"your_jwt_token\"}), 200\n    return jsonify({\"message\": \"Invalid credentials.\"}), 401\n",
                        "action": "login_user",
                        "suggested_workflow": [{
                            "start_state": "user_not_created",
                            "end_state": "user_created",
                            "action": "login_user",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    username = data.get('username')\n    password = data.get('password')\n    if username in users and users[username]['password'] == password:\n        return jsonify({\"token\": \"your_jwt_token\"}), 200\n    return jsonify({\"message\": \"Invalid credentials.\"}), 401\n",
                            "description": "Create a new user.",
                            "related_secondary_entities": []
                        }]
                    }
                ],
                "GET": [
                    {
                        "endpoint": "/user/<id>",
                        "description": "Retrieve a user by ID.",
                        "complete_code_for_action_derived_from_the_prototype": ""
                    },
                    {
                        "endpoint": "/users",
                        "description": "Retrieve all users entries.",
                        "complete_code_for_action_derived_from_the_prototype": ""
                    }
                ]
            }
        },
        {
            "entity_name": "post",
            "endpoints": {
                "POST": [
                    {
                        "endpoint": "/posts",
                        "description": "Create a new post.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    post_id = str(len(posts) + 1)\n    posts[post_id] = {\n        \"post_id\": post_id,\n        \"title\": data.get('title'),\n        \"topics\": data.get('topics'),\n        \"body\": data.get('body'),\n        \"upvotes\": 0,\n        \"downvotes\": 0\n    }\n    return jsonify({\"post_id\": post_id, \"message\": \"Post created successfully.\"}), 201\n",
                        "action": "create_post",
                        "suggested_workflow": [{
                            "start_state": "post_not_created",
                            "end_state": "post_created",
                            "action": "create_post",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    post_id = str(len(posts) + 1)\n    posts[post_id] = {\n        \"post_id\": post_id,\n        \"title\": data.get('title'),\n        \"topics\": data.get('topics'),\n        \"body\": data.get('body'),\n        \"upvotes\": 0,\n        \"downvotes\": 0\n    }\n    return jsonify({\"post_id\": post_id, \"message\": \"Post created successfully.\"}), 201\n",
                            "description": "Create a new post.",
                            "related_secondary_entities": []
                        }]
                    }
                ],
                "GET": [
                    {
                        "endpoint": "/posts",
                        "description": "Retrieve post information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    limit = request.args.get('limit', default=20, type=int)\n    offset = request.args.get('offset', default=0, type=int)\n    return jsonify({\"posts\": list(posts.values())[offset:offset + limit]}), 200\n"
                    },
                    {
                        "endpoint": "/posts/<post_id>",
                        "description": "Retrieve post information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    post = posts.get(post_id)\n    if post:\n        return jsonify(post), 200\n    return jsonify({\"message\": \"Post not found.\"}), 404\n"
                    },
                    {
                        "endpoint": "/posts/<post_id>",
                        "description": "Retrieve post information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    if post_id in posts:\n        del posts[post_id]\n        return jsonify({\"message\": \"Post deleted successfully.\"}), 200\n    return jsonify({\"message\": \"Post not found.\"}), 404\n"
                    }
                ]
            }
        },
        {
            "entity_name": "comment",
            "endpoints": {
                "POST": [
                    {
                        "endpoint": "/posts/<post_id>/comments",
                        "description": "Create a new comment.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    comment_id = str(len(comments) + 1)\n    comments[comment_id] = {\n        \"comment_id\": comment_id,\n        \"body\": data.get('body'),\n        \"post_id\": post_id,\n        \"upvotes\": 0,\n        \"downvotes\": 0\n    }\n    return jsonify({\"comment_id\": comment_id, \"message\": \"Comment added successfully.\"}), 201\n",
                        "action": "add_comment",
                        "suggested_workflow": [{
                            "start_state": "comment_not_created",
                            "end_state": "comment_created",
                            "action": "add_comment",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    comment_id = str(len(comments) + 1)\n    comments[comment_id] = {\n        \"comment_id\": comment_id,\n        \"body\": data.get('body'),\n        \"post_id\": post_id,\n        \"upvotes\": 0,\n        \"downvotes\": 0\n    }\n    return jsonify({\"comment_id\": comment_id, \"message\": \"Comment added successfully.\"}), 201\n",
                            "description": "Create a new comment.",
                            "related_secondary_entities": []
                        }]
                    }
                ],
                "GET": [
                    {
                        "endpoint": "/posts/<post_id>/comments",
                        "description": "Retrieve comment information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    post_comments = [comment for comment in comments.values() if comment['post_id'] == post_id]\n    return jsonify({\"comments\": post_comments}), 200\n"
                    },
                    {
                        "endpoint": "/posts/<post_id>/comments/<comment_id>",
                        "description": "Retrieve comment information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    if comment_id in comments and comments[comment_id]['post_id'] == post_id:\n        del comments[comment_id]\n        return jsonify({\"message\": \"Comment deleted successfully.\"}), 200\n    return jsonify({\"message\": \"Comment not found.\"}), 404\n"
                    }
                ]
            }
        },
        {
            "entity_name": "image",
            "endpoints": {
                "POST": [
                    {
                        "endpoint": "/posts/<post_id>/images",
                        "description": "Create a new image.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    image_id = str(len(images) + 1)\n    images[image_id] = {\"post_id\": post_id, \"image_data\": \"mock_image_data\"}\n    return jsonify({\"image_id\": image_id, \"message\": \"Image uploaded successfully.\"}), 201\n",
                        "action": "upload_image",
                        "suggested_workflow": [{
                            "start_state": "image_not_created",
                            "end_state": "image_created",
                            "action": "upload_image",
                            "complete_code_for_action_derived_from_the_prototype": "\n    image_id = str(len(images) + 1)\n    images[image_id] = {\"post_id\": post_id, \"image_data\": \"mock_image_data\"}\n    return jsonify({\"image_id\": image_id, \"message\": \"Image uploaded successfully.\"}), 201\n",
                            "description": "Create a new image.",
                            "related_secondary_entities": []
                        }]
                    }
                ],
                "GET": [
                    {
                        "endpoint": "/posts/<post_id>/images/<image_id>",
                        "description": "Retrieve image information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    if image_id in images and images[image_id]['post_id'] == post_id:\n        return jsonify(images[image_id]), 200\n    return jsonify({\"message\": \"Image not found.\"}), 404\n"
                    }
                ]
            }
        },
        {
            "entity_name": "vote",
            "endpoints": {
                "POST": [
                    {
                        "endpoint": "/posts/<post_id>/vote",
                        "description": "Create a new vote.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    vote = data.get('vote')\n    if vote not in ['up', 'down']:\n        return jsonify({\"message\": \"Invalid vote.\"}), 400\n    if vote == 'up':\n        posts[post_id]['upvotes'] += 1\n    else:\n        posts[post_id]['downvotes'] += 1\n    return jsonify({\"message\": \"Vote recorded.\"}), 200\n",
                        "action": "vote_post",
                        "suggested_workflow": [{
                            "start_state": "vote_not_created",
                            "end_state": "vote_created",
                            "action": "vote_post",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    vote = data.get('vote')\n    if vote not in ['up', 'down']:\n        return jsonify({\"message\": \"Invalid vote.\"}), 400\n    if vote == 'up':\n        posts[post_id]['upvotes'] += 1\n    else:\n        posts[post_id]['downvotes'] += 1\n    return jsonify({\"message\": \"Vote recorded.\"}), 200\n",
                            "description": "Create a new vote.",
                            "related_secondary_entities": []
                        }]
                    },
                    {
                        "endpoint": "/posts/<post_id>/comments/<comment_id>/vote",
                        "description": "Create a new vote.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    vote = data.get('vote')\n    if vote not in ['up', 'down']:\n        return jsonify({\"message\": \"Invalid vote.\"}), 400\n    if vote == 'up':\n        comments[comment_id]['upvotes'] += 1\n    else:\n        comments[comment_id]['downvotes'] += 1\n    return jsonify({\"message\": \"Vote recorded.\"}), 200\n",
                        "action": "vote_comment",
                        "suggested_workflow": [{
                            "start_state": "vote_not_created",
                            "end_state": "vote_created",
                            "action": "vote_comment",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.json\n    vote = data.get('vote')\n    if vote not in ['up', 'down']:\n        return jsonify({\"message\": \"Invalid vote.\"}), 400\n    if vote == 'up':\n        comments[comment_id]['upvotes'] += 1\n    else:\n        comments[comment_id]['downvotes'] += 1\n    return jsonify({\"message\": \"Vote recorded.\"}), 200\n",
                            "description": "Create a new vote.",
                            "related_secondary_entities": []
                        }]
                    }
                ],
                "GET": [
                    {
                        "endpoint": "/vote/<id>",
                        "description": "Retrieve a vote by ID.",
                        "complete_code_for_action_derived_from_the_prototype": ""
                    },
                    {
                        "endpoint": "/votes",
                        "description": "Retrieve all votes entries.",
                        "complete_code_for_action_derived_from_the_prototype": ""
                    }
                ]
            }
        }
    ],
    "secondary_entities": []
}
        expected_result = json.dumps(expected_result_json, indent=4)
        self.assertEqual(result, expected_result)


    def test_question_enqueues_event_binance(self):
        content = """
# ```python
from quart import Quart, request, jsonify
from quart_schema import QuartSchema
import aiohttp
import asyncio
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# Mock database for storing reports
reports_db = {}

# Real API URL to fetch Bitcoin conversion rates
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,eur"

async def fetch_conversion_rates():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CRYPTO_API_URL) as response:
                response.raise_for_status()  # Raise an error for bad responses
                data = await response.json()
                return {
                    "btc_usd": data['bitcoin']['usd'],
                    "btc_eur": data['bitcoin']['eur']
                }
    except Exception as e:
        logging.error(f"Error fetching conversion rates: {e}")
        return None

@app.route('/job', methods=['POST'])
async def create_report():
    data = await request.get_json()
    email = data.get('email')  # Extract user email from request data

    conversion_rates = await fetch_conversion_rates()

    if conversion_rates is None:
        return jsonify({"error": "Failed to fetch conversion rates."}), 500

    # Generate a report ID (simple incremental for prototype)
    report_id = len(reports_db) + 1
    report = {
        "id": report_id,
        "btc_usd": conversion_rates['btc_usd'],
        "btc_eur": conversion_rates['btc_eur'],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Store the report in the mock database
    reports_db[report_id] = report

    # Log the email sending action
    logging.info(f"Sending email to {email} with report ID: {report_id}. (Email sending logic not implemented)")

    return jsonify({"message": "Report creation initiated.", "reportId": report_id})

@app.route('/report/<int:id>', methods=['GET'])
async def get_report(id):
    report = reports_db.get(id)
    if report:
        return jsonify(report)
    return jsonify({"error": "Report not found."}), 404

@app.route('/reports', methods=['GET'])
async def get_reports():
    return jsonify(list(reports_db.values()))

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
# ```
    """

        endpoints = extract_endpoints(content)
        spec = generate_spec(endpoints)
        result = json.dumps(spec, indent=4)
        expected_result_json = {
    "primary_entities": [
        {
            "entity_name": "job",
            "endpoints": {
                "POST": [
                    {
                        "endpoint": "/job",
                        "description": "Create a new job.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    email = data.get('email')  # Extract user email from request data\n\n    conversion_rates = await fetch_conversion_rates()\n\n    if conversion_rates is None:\n        return jsonify({\"error\": \"Failed to fetch conversion rates.\"}), 500\n\n    # Generate a report ID (simple incremental for prototype)\n    report_id = len(reports_db) + 1\n    report = {\n        \"id\": report_id,\n        \"btc_usd\": conversion_rates['btc_usd'],\n        \"btc_eur\": conversion_rates['btc_eur'],\n        \"timestamp\": datetime.utcnow().isoformat() + \"Z\"\n    }\n\n    # Store the report in the mock database\n    reports_db[report_id] = report\n\n    # Log the email sending action\n    logging.info(f\"Sending email to {email} with report ID: {report_id}. (Email sending logic not implemented)\")\n\n    return jsonify({\"message\": \"Report creation initiated.\", \"reportId\": report_id})\n",
                        "action": "create_report",
                        "suggested_workflow": [{
                            "start_state": "job_not_created",
                            "end_state": "job_created",
                            "action": "create_report",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    email = data.get('email')  # Extract user email from request data\n\n    conversion_rates = await fetch_conversion_rates()\n\n    if conversion_rates is None:\n        return jsonify({\"error\": \"Failed to fetch conversion rates.\"}), 500\n\n    # Generate a report ID (simple incremental for prototype)\n    report_id = len(reports_db) + 1\n    report = {\n        \"id\": report_id,\n        \"btc_usd\": conversion_rates['btc_usd'],\n        \"btc_eur\": conversion_rates['btc_eur'],\n        \"timestamp\": datetime.utcnow().isoformat() + \"Z\"\n    }\n\n    # Store the report in the mock database\n    reports_db[report_id] = report\n\n    # Log the email sending action\n    logging.info(f\"Sending email to {email} with report ID: {report_id}. (Email sending logic not implemented)\")\n\n    return jsonify({\"message\": \"Report creation initiated.\", \"reportId\": report_id})\n",
                            "description": "Create a new job.",
                            "related_secondary_entities": []
                        }]
                    }
                ],
                "GET": [
                    {
                        "endpoint": "/job/<id>",
                        "description": "Retrieve a job by ID.",
                        "complete_code_for_action_derived_from_the_prototype": ""
                    },
                    {
                        "endpoint": "/jobs",
                        "description": "Retrieve all jobs entries.",
                        "complete_code_for_action_derived_from_the_prototype": ""
                    }
                ]
            }
        }
    ],
    "secondary_entities": [
        {
            "entity_name": "report",
            "endpoints": {
                "GET": [
                    {
                        "endpoint": "/report/<int:id>",
                        "description": "Retrieve report information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    report = reports_db.get(id)\n    if report:\n        return jsonify(report)\n    return jsonify({\"error\": \"Report not found.\"}), 404\n"
                    },
                    {
                        "endpoint": "/reports",
                        "description": "Retrieve report information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    return jsonify(list(reports_db.values()))\n"
                    }
                ]
            }
        }
    ]
}
        expected_result = json.dumps(expected_result_json, indent=4)
        self.assertEqual(result, expected_result)

