#!/usr/bin/env python3
"""
This script validates that the provided API code implements endpoints
as described in a JSON schema. It does not rely on function names,
but rather verifies that for each endpoint:
  - A route decorator is present with the expected URL and HTTP method.
  - The corresponding function block contains the expected service call.

For POST endpoints, it checks for a call like:

    entity_service.add_item(
        token=cyoda_token, entity_model=ENTITY_NAME_VAR, entity_version=ENTITY_VERSION, entity=data
    )

For PUT endpoints, it checks for a call like:

    entity_service.update_item(
        token=cyoda_token, entity_model=ENTITY_NAME_VAR, entity_version=ENTITY_VERSION, entity=data
    )

where ENTITY_NAME_VAR is replaced by the entity name from the schema.
"""

import re


def validate_api_code(schema: dict, code_text: str) -> list:
    """
    Validate that the code_text contains implementations for the endpoints
    described in the schema. For each endpoint, this function:
      - Searches for a route decorator that includes the expected endpoint URL and HTTP method.
      - Extracts the subsequent function block and checks for the expected service call.

    Returns a list of error messages (empty if no errors are found).
    """
    errors = []
    entity_name = schema.get("entity_name", "entity")
    endpoints = schema.get("endpoints", {})

    # Build expected patterns for POST and PUT endpoints.
    expected_post_pattern = (
            r"entity_service\.add_item\(\s*"
            r"token\s*=\s*cyoda_token\s*,\s*"
            r"entity_model\s*=\s*" + re.escape(entity_name) + r"\s*,\s*"
                                                              r"entity_version\s*=\s*ENTITY_VERSION\s*,\s*"
                                                              r"entity\s*=\s*data\s*"
                                                              r"\)"
    )
    expected_put_pattern = (
            r"entity_service\.update_item\(\s*"
            r"token\s*=\s*cyoda_token\s*,\s*"
            r"entity_model\s*=\s*" + re.escape(entity_name) + r"\s*,\s*"
                                                              r"entity_version\s*=\s*ENTITY_VERSION\s*,\s*"
                                                              r"entity\s*=\s*data\s*"
                                                              r"\)"
    )

    for method, endpoints_list in endpoints.items():
        for ep in endpoints_list:
            route = ep.get("endpoint", f"/{entity_name}")

            # Build a regex to find the route decorator.
            route_pattern = (
                rf"@[\w_]+\s*\.route\(\s*['\"]{re.escape(route)}['\"]\s*,\s*methods\s*="
                rf"\s*\[\s*['\"]{method.upper()}['\"]\s*\]\s*\)"
            )
            route_match = re.search(route_pattern, code_text)
            if not route_match:
                errors.append(
                    f"Route decorator for endpoint '{route}' with method '{method.upper()}' not found."
                )
                continue

            # Extract the function block following the decorator.
            start_index = route_match.end()
            remaining_text = code_text[start_index:]
            # Assume the function block continues until the next decorator or EOF.
            function_block = re.split(r'^\s*@', remaining_text, maxsplit=1, flags=re.MULTILINE)[0]

            if method.upper() == "POST":
                # For POST endpoints, expect add_item call.
                if not re.search(expected_post_pattern, function_block, flags=re.DOTALL):
                    errors.append(
                        f"In endpoint '{route}' (POST), expected add_item call with parameters:\n"
                        f"  token=cyoda_token, entity_model={entity_name}, entity_version=ENTITY_VERSION, entity=data\n"
                        f"not found."
                    )
            elif method.upper() == "PUT":
                # For PUT endpoints, expect update_item call.
                if not re.search(expected_put_pattern, function_block, flags=re.DOTALL):
                    errors.append(
                        f"In endpoint '{route}' (PUT), expected update_item call with parameters:\n"
                        f"  token=cyoda_token, entity_model={entity_name}, entity_version=ENTITY_VERSION, entity=data\n"
                        f"not found."
                    )
            elif method.upper() == "GET":
                # For GET endpoints, check for either get_item (if parameter exists) or get_items.
                if "<" in route and ">" in route:
                    expected_get_pattern = r"entity_service\.get_item\("
                else:
                    expected_get_pattern = r"entity_service\.get_items\("
                if not re.search(expected_get_pattern, function_block):
                    errors.append(
                        f"In endpoint '{route}' (GET), expected service call matching pattern "
                        f"'{expected_get_pattern}' not found."
                    )
                # Also check for the entity_model reference.
                entity_model_pattern = rf"entity_model\s*=\s*{re.escape(entity_name)}\b"
                if not re.search(entity_model_pattern, function_block):
                    errors.append(
                        f"In endpoint '{route}' (GET), expected entity_model reference '{entity_name}' not found."
                    )
            # Additional method validations (e.g., DELETE) can be added here if needed.

    return errors


def main():
    # Define the schema as a Python dictionary.
    schema = {
        "entity_name": "job",
        "endpoints": {
            "POST": [
                {
                    "endpoint": "/job",
                    "description": "Create a new job."
                }
            ],
            "PUT": [
                {
                    "endpoint": "/job",
                    "description": "Update an existing job."
                }
            ],
            "GET": [
                {
                    "endpoint": "/job/<job_id>",
                    "description": "Retrieve a job by job_id."
                }
            ]
        }
    }

    # Example API code as a string.
    code_text = """
from quart import Blueprint, request, jsonify
from app_init.app_init import entity_service, cyoda_token
from common.config.config import ENTITY_VERSION
import uuid
import asyncio

api_bp_job = Blueprint('api/job', __name__)

@api_bp_job.route('/job', methods=['POST'])
async def add_job():
    data = await request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        job_id = await entity_service.add_item(
            token=cyoda_token,
            entity_model=job,
            entity_version=ENTITY_VERSION,
            entity=data
        )
        return jsonify({"job_id": job_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp_job.route('/job', methods=['PUT'])
async def update_job():
    data = await request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        job_id = await entity_service.update_item(
            token=cyoda_token,
            entity_model=job,
            entity_version=ENTITY_VERSION,
            entity=data
        )
        return jsonify({"job_id": job_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp_job.route('/job/<job_id>', methods=['GET'])
async def get_job(job_id):
    try:
        data = await entity_service.get_item(
            token=cyoda_token,
            entity_model=job,
            entity_version=ENTITY_VERSION,
            id=job_id
        )
        return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

    # Run validation.
    errors = validate_api_code(schema, code_text)
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(" -", error)
    else:
        print("Code validation successful. All endpoints match the schema.")


if __name__ == "__main__":
    main()
