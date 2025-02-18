#!/usr/bin/env python3
"""
This tool reads a JSON schema that defines an entity and its endpoints,
and then generates an api.py file based on a template.

Example schema (the "suggested_workflow" field is ignored):

{
    "entity_name": "job",
    "endpoints": {
        "POST": [
            {
                "endpoint": "/job",
                "description": "Create a report for Bitcoin conversion rates and send via email."
            }
        ],
        "GET": [
            {
                "endpoint": "/report/<report_id>",
                "description": "Retrieve the report based on report ID."
            }
        ]
    }
}
"""

import argparse
import json
import re


def generate_api_code(schema: dict) -> str:
    """
    Generate the content of api.py from the input schema.
    This generator ignores any "suggested_workflow" content and always uses
    default template code based on the HTTP method.
    """
    entity_name = schema.get("entity_name", "entity")
    bp_var = f"api_bp_{entity_name}"
    lines = []

    # Standard imports and blueprint creation
    lines.append("from quart import Blueprint, request, jsonify")
    lines.append("from app_init.app_init import entity_service, cyoda_token")
    lines.append("from common.config.config import ENTITY_VERSION")
    lines.append("import uuid")
    lines.append("import asyncio")
    lines.append("")
    lines.append(f"{bp_var} = Blueprint('api/{entity_name}', __name__)")
    lines.append("")
    lines.append(f"ENTITY_MODEL = '{entity_name}'")
    lines.append("")

    endpoints = schema.get("endpoints", {})

    # Process each HTTP method and its endpoints
    for method, ep_list in endpoints.items():
        for ep in ep_list:
            route = ep.get("endpoint", f"/{entity_name}")
            description = ep.get("description", "")
            # Extract any URL parameters (e.g. <report_id> or <int:id>) for function signature
            # This regex ignores the type (if present) and only captures the parameter name.
            params = re.findall(r'<(?:[^:]+:)?([^>]+)>', route)
            params_str = ", ".join(params) if params else ""

            # Create a function name based on HTTP method and route information
            if method.upper() == "POST":
                func_name = f"add_{entity_name}"
            elif method.upper() == "PUT":
                func_name = f"update_{entity_name}"
            elif method.upper() == "GET":
                # If the route has a parameter, use it in the function name
                if params:
                    func_name = f"get_{params[0]}"
                else:
                    func_name = f"get_{entity_name}s"
            elif method.upper() == "DELETE":
                func_name = f"delete_{entity_name}"
            else:
                func_name = f"{method.lower()}_{entity_name}"

            # Add the route decorator and function definition
            lines.append(f"@{bp_var}.route('{route}', methods=['{method.upper()}'])")
            lines.append(f"async def {func_name}({params_str}):")
            lines.append(f'    """{description}"""')

            # Generate code based on the HTTP method (ignoring any suggested_workflow)
            if method.upper() == "POST":
                lines.append("    data = await request.json")
                lines.append("    if not data:")
                lines.append("        return jsonify({\"error\": \"No data provided\"}), 400")
                lines.append("    try:")
                lines.append(f"        {entity_name}_id = await entity_service.add_item(")
                lines.append("            token=cyoda_token,")
                lines.append(f"            entity_model=ENTITY_MODEL,")
                lines.append("            entity_version=ENTITY_VERSION,")
                lines.append("            entity=data")
                lines.append("        )")
                lines.append(f"        return jsonify({{'{entity_name}_id': {entity_name}_id}}), 201")
                lines.append("    except Exception as e:")
                lines.append("        return jsonify({\"error\": str(e)}), 500")

            elif method.upper() == "PUT":
                lines.append("    data = await request.json")
                lines.append("    if not data:")
                lines.append("        return jsonify({\"error\": \"No data provided\"}), 400")
                lines.append("    try:")
                lines.append(f"        {entity_name}_id = await entity_service.add_item(")
                lines.append("            token=cyoda_token,")
                lines.append(f"            entity_model=ENTITY_MODEL,")
                lines.append("            entity_version=ENTITY_VERSION,")
                lines.append("            technical_id=data.get('id'),")
                lines.append("            entity=data")
                lines.append("        )")
                lines.append(f"        return jsonify({{'{entity_name}_id': {entity_name}_id}}), 201")
                lines.append("    except Exception as e:")
                lines.append("        return jsonify({\"error\": str(e)}), 500")

            elif method.upper() == "GET":
                if params:
                    # For routes with a URL parameter, assume a single item retrieval
                    param = params[0]
                    lines.append("    try:")
                    lines.append(f"        data = await entity_service.get_item(")
                    lines.append("            token=cyoda_token,")
                    lines.append(f"            entity_model=ENTITY_MODEL,")
                    lines.append("            entity_version=ENTITY_VERSION,")
                    lines.append(f"            technical_id={param}")
                    lines.append("        )")
                    lines.append("        return jsonify({\"data\": data}), 200")
                    lines.append("    except Exception as e:")
                    lines.append("        return jsonify({\"error\": str(e)}), 500")
                else:
                    # For routes without parameters, assume retrieval of multiple items
                    lines.append("    try:")
                    lines.append(f"        data = await entity_service.get_items(")
                    lines.append("            token=cyoda_token,")
                    lines.append(f"            entity_model=ENTITY_MODEL,")
                    lines.append("            entity_version=ENTITY_VERSION")
                    lines.append("        )")
                    lines.append("        return jsonify({\"data\": data}), 200")
                    lines.append("    except Exception as e:")
                    lines.append("        return jsonify({\"error\": str(e)}), 500")

            elif method.upper() == "DELETE":
                lines.append("    try:")
                lines.append("        # Implement deletion logic here")
                lines.append("        return jsonify({\"message\": \"Deleted\"}), 200")
                lines.append("    except Exception as e:")
                lines.append("        return jsonify({\"error\": str(e)}), 500")
            else:
                lines.append("    return jsonify({\"message\": \"Not implemented\"}), 501")

            lines.append("")  # Blank line between endpoint definitions

    return "\n".join(lines)


def main():
    schema = {
            "entity_name": "report",
            "endpoints": {
                "GET": [
                    {
                        "endpoint": "/reports/<report_id>",
                        "description": "Retrieve report information.",
                        "complete_code_for_action_derived_from_the_prototype": "\n    report = reports.get(report_id)\n    if not report:\n        return jsonify({\"error\": \"Report not found.\"}), 404\n    return jsonify({\n        \"id\": report_id,\n        \"btc_usd_rate\": report[\"btc_usd_rate\"],\n        \"btc_eur_rate\": report[\"btc_eur_rate\"],\n        \"timestamp\": report[\"timestamp\"]\n    }), 200\n"
                    }
                ]
            }
        }
    result = generate_api_code(schema)
    print(result)


if __name__ == "__main__":
    main()
