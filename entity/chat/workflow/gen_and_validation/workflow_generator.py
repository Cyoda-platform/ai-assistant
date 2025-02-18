def generate_workflow_code(schema):
    """
    Generates Python code based on the provided schema and the following rules:
      - Includes fixed import statements and logging setup.
      - Creates an async function for each workflow action.
      - Inserts the provided "complete_code_for_action_derived_from_the_prototype" inside a try block.
      - Appends commented-out code for handling each secondary entity.
      - Comments out all lines in the function body (i.e. after the header and docstring).
      - Adds the except block that logs errors.

    The schema is expected to be a dict with a key "suggested_workflow" whose value is a list of steps.
    Each step may include:
      - action: Name of the action (function name).
      - complete_code_for_action_derived_from_the_prototype: The core code to insert.
      - related_secondary_entities: A list of secondary entity names.
      - description: (Optional) description to include in the function's docstring.
    """
    lines = []

    # Fixed imports and logging setup
    lines.append("import json")
    lines.append("import logging")
    lines.append("from aiohttp import ClientSession")

    # Append the entity_service import only if any step uses related_secondary_entities.
    if any(step.get("related_secondary_entities", []) for step in schema):
        lines.append("from app_init.app_init import entity_service")
        lines.append("from common.config.config import ENTITY_VERSION")
    lines.append("")
    lines.append("logging.basicConfig(level=logging.INFO)")
    lines.append("logger = logging.getLogger(__name__)")
    lines.append("")

    # Process each workflow step in the schema
    for step in schema:
        action = step.get("action", "action_name")
        description = step.get("description", "Complete business logic")
        complete_code = step.get("complete_code_for_action_derived_from_the_prototype", "").rstrip()
        secondary_entities = step.get("related_secondary_entities", [])

        # Function header and docstring (not commented out)
        lines.append(f"async def {action}(data, meta={{'token': 'cyoda_token'}}):")
        lines.append("    \"\"\"")
        lines.append(f"    {description}")
        lines.append("")
        lines.append("    Complete business logic")
        lines.append("    \"\"\"")

        # Begin building the function body (which we will comment out entirely)
        func_body = []
        func_body.append("try:")
        # Insert the provided complete code (indent each line with 4 additional spaces)
        if complete_code:
            for code_line in complete_code.splitlines():
                func_body.append("    " + code_line)
        else:
            func_body.append("    pass")
        func_body.append("")

        # Append commented-out code for handling secondary entities, if any
        if secondary_entities:
            func_body.append(
                "    # The following commented-out code shows how to save and retrieve secondary entities:")
            for entity in secondary_entities:
                func_body.append(
                    "    # We are migrating prototype.py code to production ready workflow code so any in-memory caches if relevant - should be replaced with specified entity_service methods.")
                func_body.append(
                    f"    # {entity}_id = await entity_service.add_item(token=meta['token'], entity_model='{entity}', entity_version=ENTITY_VERSION, entity={entity}_data)")
                func_body.append(
                    f"    # {entity}_data = await entity_service.get_item(token=meta['token'], entity_model='{entity}', entity_version=ENTITY_VERSION, technical_id={entity}_id)")
                func_body.append(
                    "    # Don't forget to add a reference to the just saved secondary entity to the primary entity data - so that we can track the results: ")
                func_body.append(f"    # data['{entity}_id'] = {entity}_id")
            func_body.append(" ")
            func_body.append("    # Optionally update the current entity data with calculated results: ")
            func_body.append("    # data['attribute'] = calculated_value")
            func_body.append("")

        # Append the except block exactly as specified
        func_body.append("except Exception as e:")
        func_body.append("    logger.error(f\"Error in send_teamcity_request: {e}\")")
        func_body.append("    raise")

        # Now comment out every line of the function body.
        # We insert the function-level indent (4 spaces) and then "# " before the original content.
        for line in func_body:
            # Even blank lines get a comment marker for consistency.
            if line.strip() == "":
                lines.append("    #")
            else:
                lines.append("    # " + line)
        lines.append("")  # Blank line after function

    # Return the generated code as a single string
    return "\n".join(lines)


# -------------------------------------
# Example usage:
# -------------------------------------
if __name__ == "__main__":
    # Example schema input – replace with your own schema as needed.
    example_schema = [
        {
            "start_state": "post_not_created",
            "end_state": "post_created",
            "action": "create_post",
            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    post_id = generate_id(mock_posts)\n    mock_posts[post_id] = {\n        'title': data['title'],\n        'body': data['body'],\n        'topics': data['topics'],\n        'user_id': data.get('user_id', '1')  # TODO: Get actual user_id when auth is implemented\n    }\n    return jsonify({\"post_id\": post_id, \"message\": \"Post created successfully\"})\n",
            "description": "Create a new post.",
            "related_secondary_entities": []
        }
    ]

    # Generate the code based on the provided schema
    generated_code = generate_workflow_code(example_schema)

    # For demonstration purposes, print the generated code
    print(generated_code)
