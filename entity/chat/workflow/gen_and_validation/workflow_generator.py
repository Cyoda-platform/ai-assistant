import re
import inflect


def generate_workflow_code(schema, entity_name):
    """
    Generates Python code based on the provided schema and the following rules:
      - Includes fixed import statements and logging setup.
      - Creates an async function for each workflow action.
      - Inserts the provided "complete_code_for_action_derived_from_the_prototype" inside a try block.
      - Appends commented-out code for handling each secondary entity (only if the secondary entity
        is different from the primary entity, considering both singular and plural forms).
      - Comments out all lines in the function body (i.e. after the header and docstring).
      - Adds the except block that logs errors.

    The schema is expected to be a list of steps.
    Each step may include:
      - action: Name of the action (function name).
      - complete_code_for_action_derived_from_the_prototype: The core code to insert.
      - related_secondary_entities: A list of secondary entity names.
      - description: (Optional) description to include in the function's docstring.
    """
    p = inflect.engine()
    plural_entity_name = p.plural(entity_name)

    lines = []

    # Fixed imports and logging setup
    lines.append("import json")
    lines.append("import logging")
    lines.append("from aiohttp import ClientSession")

    # Append the entity_service import only if there is any secondary entity that is not the primary entity
    # (comparing both singular and plural forms)
    if any(s for step in schema for s in step.get("related_secondary_entities", []) if
           s not in (entity_name, plural_entity_name)):
        lines.append("from app_init.app_init import entity_service")
        lines.append("from common.config.config import ENTITY_VERSION")
    lines.append("")
    lines.append("logging.basicConfig(level=logging.INFO)")
    lines.append("logger = logging.getLogger(__name__)")
    lines.append("")
    lines.append(f"ENTITY_MODEL = '{entity_name}'")
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

        # Process the provided complete code.
        # Remove any usage of entity_service where entity_model equals either the singular or plural primary entity.
        if complete_code:
            # The trailing whitespace match (\s*) is replaced with a lookahead (?=[ \t]*(?:\n|$))
            # so that we do not consume the newline following the call.
            pattern = re.compile(
                r'(?:\s*\w+\s*=\s*)?await\s+entity_service\.\w+\(.*?entity_model\s*=\s*["\'](?:{}|{})["\'].*?\)(?=[ \t]*(?:\n|$))'.format(
                    re.escape(entity_name), re.escape(plural_entity_name)
                ),
                re.DOTALL
            )
            filtered_code = pattern.sub("", complete_code)
            for code_line in filtered_code.splitlines():
                # Remove lines that contain "await request.get" or start with a return statement.
                if "request." in code_line:
                    continue
                if re.match(r'^\s*return\b', code_line):
                    continue
                func_body.append("    " + code_line)
        else:
            func_body.append("    pass")
        func_body.append("")

        # Append commented-out code for handling secondary entities (only those not equal to the primary entity in either form)
        filtered_secondary_entities = [
            e for e in secondary_entities if e not in (entity_name, plural_entity_name)
        ]
        if filtered_secondary_entities:
            func_body.append("    # The following commented-out code shows how to save and retrieve secondary entities:")
            for entity in filtered_secondary_entities:
                func_body.append("    # We are migrating prototype.py code to production ready workflow code so any in-memory caches if relevant - should be replaced with specified entity_service methods.")
                func_body.append(f"    # {entity}_id = await entity_service.add_item(token=meta['token'], entity_model='{entity}', entity_version=ENTITY_VERSION, entity={entity}_data)")
                func_body.append(f"    # {entity}_data = await entity_service.get_item(token=meta['token'], entity_model='{entity}', entity_version=ENTITY_VERSION, technical_id={entity}_id)")
                func_body.append("    # Don't forget to add a reference to the just saved secondary entity to the primary entity data - so that we can track the results: ")
                func_body.append(f"    # data['{entity}_id'] = {entity}_id")
            func_body.append(" ")
            func_body.append("    # Optionally update the current entity data with calculated results: ")
            func_body.append("    # data['attribute'] = calculated_value")
            func_body.append("")

        # Append the except block exactly as specified
        func_body.append("except Exception as e:")
        func_body.append("    logger.exception(e)")
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
            "start_state": "article_not_created",
            "end_state": "article_created",
            "action": "create_article",
            "complete_code_for_action_derived_from_the_prototype": """
    data = await request.get_json()
    validate_article(data)
    created_item = await entity_service.add_item(
        token=token,
        entity_model="article",  # or "articles" for plural usage
        entity_version=ENTITY_VERSION,
        entity=data
    )
    return jsonify(created_item), 201
""",
            "description": "Create a new article.",
            "related_secondary_entities": ['report']  # No secondary entities in this example.
        }
    ]

    # Generate the code based on the provided schema
    entity_name = 'articlehs'
    generated_code = generate_workflow_code(example_schema, entity_name)

    # For demonstration purposes, print the generated code
    print(generated_code)
