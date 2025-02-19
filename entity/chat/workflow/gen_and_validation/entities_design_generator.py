import re
import json
import sys
import inflect
import nltk
from nltk.corpus import wordnet as wn

# Ensure WordNet is downloaded (only needed once)
nltk.download('wordnet', quiet=True)

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


def is_noun_segment(word):
    """
    Use WordNet synset counts as a heuristic:
      - If the number of noun synsets is greater than or equal to verb synsets,
        consider the word to be noun-like.
      - If the word is not found in WordNet, assume it is a noun.
    """
    noun_syns = wn.synsets(word, pos=wn.NOUN)
    verb_syns = wn.synsets(word, pos=wn.VERB)
    if not noun_syns and not verb_syns:
        return True
    return len(noun_syns) >= len(verb_syns)


def get_endpoint_group_key(endpoint):
    """
    Determine a grouping key for an endpoint by selecting the last segment that is likely a noun.

    Steps:
      1. Split the path into segments.
      2. Remove segments that are parameters (e.g. "<post_id>") or in the exclusions set.
         Exclusions include: "api", "v1", "v2", "v3", "v4", "deploy".
      3. Iterate over the remaining segments in reverse order and select the first segment
         that is likely a noun (using WordNet synset counts).
      4. If no segment qualifies as a noun, fall back to the last segment.

    Examples:
      /user/login -> returns "user" because "login" is considered more verb-like.
      /courses/<id>/enrollments -> returns "enrollment"
      /api/hydrometric-collection -> returns "hydrometric_collection"
    """
    exclusions = {"api", "v1", "v2", "v3", "v4", "deploy"}
    segments = [seg.replace("-", "_") for seg in endpoint.strip("/").split("/")
                if seg and not re.match(r"<.*>", seg) and seg.lower() not in exclusions]
    if segments:
        # Iterate in reverse to find the first segment that is likely a noun.
        for seg in reversed(segments):
            if is_noun_segment(seg):
                return normalize_resource_name(seg)
        # Fallback if none qualify
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

    This version tracks added endpoint URLs per method to avoid duplicates.
    """
    primary_entities = {}
    secondary_entities = {}

    # For deduplication: track added endpoints for each entity and method.
    primary_endpoints_set = {}
    secondary_endpoints_set = {}

    for ep in endpoints:
        methods = ep["methods"]
        new_key = get_endpoint_group_key(ep["endpoint"])
        # If any POST method exists, treat the entity as primary.
        if "POST" in methods:
            key = new_key
            if key not in primary_entities:
                primary_entities[key] = {
                    "entity_name": key,
                    "endpoints": {"POST": [], "GET": []}
                }
                primary_endpoints_set[key] = {"POST": set(), "GET": set()}
            # Process each method for this endpoint.
            for method in methods:
                if method == "POST":
                    if ep["endpoint"] not in primary_endpoints_set[key]["POST"]:
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
                        primary_endpoints_set[key]["POST"].add(ep["endpoint"])
                elif method == "GET":
                    if ep["endpoint"] not in primary_endpoints_set[key]["GET"]:
                        primary_entities[key]["endpoints"]["GET"].append({
                            "endpoint": ep["endpoint"],
                            "description": f"Retrieve {key} information.",
                            "complete_code_for_action_derived_from_the_prototype": ep["code"]
                        })
                        primary_endpoints_set[key]["GET"].add(ep["endpoint"])
            # Merge any secondary endpoints for this entity into primary (deduplicating as well)
            if key in secondary_entities:
                for ge in secondary_entities[key]["endpoints"].get("GET", []):
                    if ge["endpoint"] not in primary_endpoints_set[key]["GET"]:
                        primary_entities[key]["endpoints"]["GET"].append(ge)
                        primary_endpoints_set[key]["GET"].add(ge["endpoint"])
                del secondary_entities[key]
                if key in secondary_endpoints_set:
                    del secondary_endpoints_set[key]
        else:
            # For endpoints that are not POST, treat as secondary if a primary hasn't been defined.
            key = new_key
            if key in primary_entities:
                if ep["endpoint"] not in primary_endpoints_set[key]["GET"]:
                    primary_entities[key]["endpoints"]["GET"].append({
                        "endpoint": ep["endpoint"],
                        "description": f"Retrieve {key} information.",
                        "complete_code_for_action_derived_from_the_prototype": ep["code"]
                    })
                    primary_endpoints_set[key]["GET"].add(ep["endpoint"])
            else:
                if key not in secondary_entities:
                    secondary_entities[key] = {
                        "entity_name": key,
                        "endpoints": {"GET": []}
                    }
                    secondary_endpoints_set[key] = {"GET": set()}
                if ep["endpoint"] not in secondary_endpoints_set[key]["GET"]:
                    secondary_entities[key]["endpoints"]["GET"].append({
                        "endpoint": ep["endpoint"],
                        "description": f"Retrieve {key} information.",
                        "complete_code_for_action_derived_from_the_prototype": ep["code"]
                    })
                    secondary_endpoints_set[key]["GET"].add(ep["endpoint"])

    # Auto-generate default GET endpoints for primary entities if none exist.
    for key, entity in primary_entities.items():
        if not entity["endpoints"]["GET"]:
            default_get1 = {
                "endpoint": f"/{key}/<id>",
                "description": f"Retrieve a {key} by ID.",
                "complete_code_for_action_derived_from_the_prototype": ""
            }
            if default_get1["endpoint"] not in primary_endpoints_set[key]["GET"]:
                entity["endpoints"]["GET"].append(default_get1)
                primary_endpoints_set[key]["GET"].add(default_get1["endpoint"])
            entity_plural = p.plural(key)
            default_get2 = {
                "endpoint": f"/{entity_plural}",
                "description": f"Retrieve all {entity_plural} entries.",
                "complete_code_for_action_derived_from_the_prototype": ""
            }
            if default_get2["endpoint"] not in primary_endpoints_set[key]["GET"]:
                entity["endpoints"]["GET"].append(default_get2)
                primary_endpoints_set[key]["GET"].add(default_get2["endpoint"])

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

from quart import Quart, jsonify, request, abort
import httpx

app = Quart(__name__)

# In‑memory “database”
articles = {}
sources = {}
topics = {}

article_id_counter = 1
source_id_counter = 1
topic_id_counter = 1

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

def validate_article(data):
    if 'title' not in data or 'content' not in data:
        abort(400, description="Article must have 'title' and 'content'")
    return data

def validate_source(data):
    if 'name' not in data:
        abort(400, description="Source must have 'name'")
    return data

def validate_topic(data):
    if 'name' not in data:
        abort(400, description="Topic must have 'name'")
    return data

# Articles endpoints
@app.route('/articles', methods=['GET'])
async def get_articles():
    await call_mock_service("GET", "posts")
    return jsonify(list(articles.values()))

@app.route('/articles/<string:articleId>', methods=['GET'])
async def get_article(articleId):
    article = articles.get(articleId)
    if not article:
        abort(404, description="Article not found")
    return jsonify(article)

@app.route('/articles', methods=['POST'])
async def create_article():
    global article_id_counter
    data = await request.get_json()
    validate_article(data)
    new_id = str(article_id_counter)
    article_id_counter += 1
    data['id'] = new_id
    articles[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

@app.route('/articles/<string:articleId>', methods=['PUT'])
async def update_article(articleId):
    if articleId not in articles:
        abort(404, description="Article not found")
    data = await request.get_json()
    validate_article(data)
    data['id'] = articleId
    articles[articleId] = data
    return jsonify(data)

@app.route('/articles/<string:articleId>', methods=['DELETE'])
async def delete_article(articleId):
    if articleId not in articles:
        abort(404, description="Article not found")
    del articles[articleId]
    return '', 204

# Sources endpoints
@app.route('/sources', methods=['GET'])
async def get_sources():
    await call_mock_service("GET", "users")
    return jsonify(list(sources.values()))

@app.route('/sources', methods=['POST'])
async def create_source():
    global source_id_counter
    data = await request.get_json()
    validate_source(data)
    new_id = str(source_id_counter)
    source_id_counter += 1
    data['id'] = new_id
    sources[new_id] = data
    await call_mock_service("POST", "users", data)
    return jsonify(data), 201

# Topics endpoints
@app.route('/topics', methods=['GET'])
async def get_topics():
    await call_mock_service("GET", "posts")
    return jsonify(list(topics.values()))

@app.route('/topics', methods=['POST'])
async def create_topic():
    global topic_id_counter
    data = await request.get_json()
    validate_topic(data)
    new_id = str(topic_id_counter)
    topic_id_counter += 1
    data['id'] = new_id
    topics[new_id] = data
    await call_mock_service("POST", "posts", data)
    return jsonify(data), 201

if __name__ == '__main__':
    app.run()


 """
    endpoints = extract_endpoints(content)
    spec = generate_spec(endpoints)
    spec = add_related_secondary_entities(spec)
    print(json.dumps(spec, indent=4))


if __name__ == "__main__":
    main()
