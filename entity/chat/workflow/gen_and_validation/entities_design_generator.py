import re
import json
import sys
import inflect

from entity.chat.workflow.gen_and_validation.entities_design_enricher import add_related_secondary_entities

# Create an inflect engine instance
p = inflect.engine()


def extract_endpoints(file_content):
    """
    Scan the file content for @app.route decorators and extract:
      - The endpoint URL.
      - The HTTP methods.
      - The function name.
      - The function body (a rough extraction).
    """
    pattern = r"@app\.route\((.*?)\)\s*(async\s+def\s+(\w+)\(.*?\):)"
    matches = re.finditer(pattern, file_content, re.DOTALL)
    endpoints = []
    for match in matches:
        decorator_args = match.group(1)
        func_name = match.group(3)
        # Extract the endpoint path (first string argument)
        path_match = re.search(r"['\"](.*?)['\"]", decorator_args)
        endpoint_path = path_match.group(1) if path_match else ""
        # Extract HTTP methods if provided; otherwise, default to GET.
        methods_match = re.search(r"methods\s*=\s*\[([^\]]+)\]", decorator_args)
        if methods_match:
            methods_str = methods_match.group(1)
            methods = re.findall(r"['\"](.*?)['\"]", methods_str)
        else:
            methods = ["GET"]
        # Naively extract the function body (all subsequent indented lines)
        start_index = match.end()
        lines = file_content[start_index:].splitlines()
        code_lines = []
        for line in lines:
            if line.strip() == "":
                code_lines.append(line)
                continue
            if re.match(r"^\s", line):
                code_lines.append(line)
            else:
                break
        function_body = "\n".join(code_lines)
        endpoints.append({
            "endpoint": endpoint_path,
            "methods": methods,
            "function_name": func_name,
            "code": function_body
        })
    return endpoints


def normalize_resource_name(resource):
    """
    Normalize a resource name using the inflect library.
    If the resource name contains underscores, singularize only the last segment
    unless that segment is in an exceptions list (e.g. "status").
    """
    exceptions = {"status"}
    parts = resource.split("_")
    if parts[-1].lower() in exceptions:
        return resource
    singular_last = p.singular_noun(parts[-1])
    if singular_last:
        parts[-1] = singular_last
        return "_".join(parts)
    else:
        return resource


def get_endpoint_group_key(endpoint):
    """
    Determine a grouping key for an endpoint in a general way:

      1. Split the path into segments.
      2. Remove any segments that are parameters (e.g. "<post_id>") or in the exclusions set.
         Exclusions include: "api", "v1", "v2", "v3", "v4", "deploy".
      3. If at least two static segments remain, return:
             normalize_resource_name(second_last_segment) + "_" + normalize_resource_name(last_segment)
         Otherwise, return the single remaining segment (normalized).

    Examples:
      /deploy/cyoda-env              -> "cyoda_env"
      /posts/<post_id>/vote          -> "post_vote"
      /posts/<post_id>/comments/<cid>/vote -> "comment_vote"
      /api/hydrometric-collection    -> "hydrometric_collection"
    """
    exclusions = {"api", "v1", "v2", "v3", "v4", "deploy"}
    segments = [seg.replace("-", "_") for seg in endpoint.strip("/").split("/")
                if seg and not re.match(r"<.*>", seg) and seg.lower() not in exclusions]
    if len(segments) >= 2:
        parent = normalize_resource_name(segments[-2])
        child = normalize_resource_name(segments[-1])
        return f"{parent}_{child}"
    elif segments:
        return normalize_resource_name(segments[-1])
    return ""


def generate_spec(endpoints):
    """
    Build a JSON spec based on the endpoints:
      - Endpoints with POST (even nested ones) are grouped as primary.
      - If an entity has any POST endpoints, all endpoints (including GET ones)
        for that entity are merged into primary.
      - GET-only endpoints for entities that never have a POST endpoint are grouped as secondary.
      - Each POST endpoint carries its own suggested workflow.
      - Finally, if a secondary (GET-only) endpoint's code references a primary entity,
        its name is added to that primary entity's related secondary entities.
    """
    primary_entities = {}
    secondary_entities = {}

    for ep in endpoints:
        methods = ep["methods"]
        new_key = get_endpoint_group_key(ep["endpoint"])
        if "POST" in methods:
            key = new_key
            if key not in primary_entities:
                primary_entities[key] = {
                    "entity_name": key,
                    "endpoints": {"POST": [], "GET": []}
                }
            for method in methods:
                if method == "POST":
                    workflow_entry = [{
                        "start_state": f"{key}_not_created",
                        "end_state": f"{key}_created",
                        "action": ep["function_name"],
                        "complete_code_for_action_derived_from_the_prototype": ep["code"],
                        "description": f"Create a new {key}.",
                        "related_secondary_entities": []
                    }]
                    primary_entities[key]["endpoints"]["POST"].append({
                        "endpoint": ep["endpoint"],
                        "description": f"Create a new {key}.",
                        "complete_code_for_action_derived_from_the_prototype": ep["code"],
                        "action": ep["function_name"],
                        "suggested_workflow": workflow_entry
                    })
                elif method == "GET":
                    primary_entities[key]["endpoints"]["GET"].append({
                        "endpoint": ep["endpoint"],
                        "description": f"Retrieve {key} information.",
                        "complete_code_for_action_derived_from_the_prototype": ep["code"]
                    })
            if key in secondary_entities:
                for ge in secondary_entities[key]["endpoints"].get("GET", []):
                    primary_entities[key]["endpoints"]["GET"].append(ge)
                del secondary_entities[key]
        else:
            key = get_endpoint_group_key(ep["endpoint"])
            if key in primary_entities:
                primary_entities[key]["endpoints"]["GET"].append({
                    "endpoint": ep["endpoint"],
                    "description": f"Retrieve {key} information.",
                    "complete_code_for_action_derived_from_the_prototype": ep["code"]
                })
            else:
                if key not in secondary_entities:
                    secondary_entities[key] = {
                        "entity_name": key,
                        "endpoints": {"GET": []}
                    }
                secondary_entities[key]["endpoints"]["GET"].append({
                    "endpoint": ep["endpoint"],
                    "description": f"Retrieve {key} information.",
                    "complete_code_for_action_derived_from_the_prototype": ep["code"]
                })

    # Auto-generate default GET endpoints for primary entities if none exist.
    for key, entity in primary_entities.items():
        if not entity["endpoints"]["GET"]:
            entity["endpoints"]["GET"].append({
                "endpoint": f"/{key}/<id>",
                "description": f"Retrieve a {key} by ID.",
                "complete_code_for_action_derived_from_the_prototype": ""
            })
            entity_plural = p.plural(key)
            entity["endpoints"]["GET"].append({
                "endpoint": f"/{entity_plural}",
                "description": f"Retrieve all {entity_plural} entries.",
                "complete_code_for_action_derived_from_the_prototype": ""
            })

    # Relate secondary GET-only entities to primary entities if their code references the primary entity name.
    for sec_key, sec_entity in secondary_entities.items():
        for get_ep in sec_entity["endpoints"].get("GET", []):
            code = get_ep["complete_code_for_action_derived_from_the_prototype"]
            for prim_key, prim_entity in primary_entities.items():
                if re.search(r"\b" + re.escape(prim_key) + r"\b", code):
                    for post_ep in prim_entity["endpoints"]["POST"]:
                        if "related_secondary_entities" not in post_ep:
                            post_ep["related_secondary_entities"] = []
                        if sec_entity["entity_name"] not in post_ep["related_secondary_entities"]:
                            post_ep["related_secondary_entities"].append(sec_entity["entity_name"])

    spec = {
        "primary_entities": list(primary_entities.values()),
        "secondary_entities": list(secondary_entities.values())
    }
    return spec


def main():
    content = """

# Here is a prototype implementation of the `prototype.py` file using Quart for your backend application. The code includes the API endpoints as specified and uses `aiohttp.ClientSession` for HTTP requests. I've incorporated placeholders and TODO comments where necessary.
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
    # TODO: Add password hashing and validation logic
    users[username] = {'password': password}
    return jsonify({"message": "User created successfully."}), 201

@app.route('/users/login', methods=['POST'])
async def login_user():
    data = await request.json
    username = data.get('username')
    password = data.get('password')
    # TODO: Add validation for username and password
    if username in users and users[username]['password'] == password:
        # TODO: Generate JWT token
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
    # TODO: Implement pagination and sorting by popularity
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
    # TODO: Implement image upload logic (e.g., save to filesystem or cloud storage)
    image_id = str(len(images) + 1)
    images[image_id] = {"post_id": post_id, "image_data": "mock_image_data"}
    return jsonify({"image_id": image_id, "message": "Image uploaded successfully."}), 201

@app.route('/posts/<post_id>/images/<image_id>', methods=['GET'])
async def get_image(post_id, image_id):
    # TODO: Implement logic to retrieve actual image data
    if image_id in images and images[image_id]['post_id'] == post_id:
        return jsonify(images[image_id]), 200
    return jsonify({"message": "Image not found."}), 404

@app.route('/posts/<post_id>/vote', methods=['POST'])
async def vote_post(post_id):
    data = await request.json
    vote = data.get('vote')
    # TODO: Implement vote counting logic
    if vote not in ['up', 'down']:
        return jsonify({"message": "Invalid vote."}), 400
    # Mock vote update
    if vote == 'up':
        posts[post_id]['upvotes'] += 1
    else:
        posts[post_id]['downvotes'] += 1
    return jsonify({"message": "Vote recorded."}), 200

@app.route('/posts/<post_id>/comments/<comment_id>/vote', methods=['POST'])
async def vote_comment(post_id, comment_id):
    data = await request.json
    vote = data.get('vote')
    # TODO: Implement vote counting logic for comments
    if vote not in ['up', 'down']:
        return jsonify({"message": "Invalid vote."}), 400
    # Mock vote update
    if vote == 'up':
        comments[comment_id]['upvotes'] += 1
    else:
        comments[comment_id]['downvotes'] += 1
    return jsonify({"message": "Vote recorded."}), 200

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
# ```
# 
# ### Important Notes
# - The prototype uses in-memory data structures (`users`, `posts`, `comments`, `images`, `votes`) for demonstration purposes. In a production application, you would typically use a database.
# - TODO comments have been added to indicate areas that require further implementation or clarification.
# - The JWT token generation and user validation logic are placeholders and need to be implemented for security.
# - Error handling and validation are minimal in this prototype to keep it focused on the core functionality.
# 
# Feel free to expand on this prototype or ask for further modifications based on your needs!

  
   """
    endpoints = extract_endpoints(content)
    spec = generate_spec(endpoints)
    spec = add_related_secondary_entities(spec)
    print(json.dumps(spec, indent=4))


if __name__ == "__main__":
    main()
