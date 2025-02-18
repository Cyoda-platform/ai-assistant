import json
import re


def add_related_secondary_entities(data):
    """
    Process the given data structure to add secondary entity references
    into the primary endpoints' `related_secondary_entities`. Two techniques are used:

    1. Look for references in the code snippets (complete_code_for_action_derived_from_the_prototype)
       by matching secondary entity names and their plural forms.

    2. Look at each secondary entity's endpoint path. If the path contains a reference to a primary
       entity (by using either the primary entity name or a slug version with underscores replaced by hyphens),
       add that secondary entity to all endpoints (and their suggested workflows) of the primary entity.
    """

    # --- Step 1: Prepare secondary entity keywords for code scanning ---
    secondary_names = set()
    for secondary in data.get("secondary_entities", []):
        name = secondary.get("entity_name", "")
        if name:
            secondary_names.add(name)

    # For each secondary entity name, consider the name and its plural form.
    secondary_keywords = {}
    for name in secondary_names:
        secondary_keywords[name] = [name, name + "s"]

    # --- Step 2: Prepare primary entity variations for matching in endpoint paths ---
    # For each primary entity, we'll consider both the original name and a "slug" version.
    primary_entity_variations = {}
    for primary in data.get("primary_entities", []):
        primary_name = primary.get("entity_name", "")
        if primary_name:
            # Create a variation where underscores are replaced by hyphens.
            slug = primary_name.replace("_", "-")
            # You might want to add more variations if your naming is inconsistent.
            primary_entity_variations[primary_name] = {primary_name, slug}

    # --- Helper function: scan code for secondary entity references ---
    def find_secondary_refs_in_code(code):
        found = set()
        for sec_name, keywords in secondary_keywords.items():
            for keyword in keywords:
                # Use word-boundaries to match whole words
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, code):
                    found.add(sec_name)
        return found

    # --- Step 3: Process primary endpoints based on code inspection ---
    for primary in data.get("primary_entities", []):
        endpoints = primary.get("endpoints", {})
        for method, endpoint_list in endpoints.items():
            for ep in endpoint_list:
                # Inspect the main code snippet
                code_snippet = ep.get("complete_code_for_action_derived_from_the_prototype", "")
                refs = find_secondary_refs_in_code(code_snippet)
                if refs:
                    related = ep.get("related_secondary_entities", [])
                    for ref in refs:
                        if ref not in related:
                            related.append(ref)
                    ep["related_secondary_entities"] = related

                # Also process any suggested workflow entries within the endpoint
                if "suggested_workflow" in ep:
                    for workflow in ep["suggested_workflow"]:
                        wf_code = workflow.get("complete_code_for_action_derived_from_the_prototype", "")
                        wf_refs = find_secondary_refs_in_code(wf_code)
                        if wf_refs:
                            related_wf = workflow.get("related_secondary_entities", [])
                            for ref in wf_refs:
                                if ref not in related_wf:
                                    related_wf.append(ref)
                            workflow["related_secondary_entities"] = related_wf

    # --- Step 4: Process secondary endpoints based on their URL paths ---
    # For each secondary entity, check if any of its endpoint paths mention a primary entity.
    for secondary in data.get("secondary_entities", []):
        sec_name = secondary.get("entity_name", "")
        for method, sec_eps in secondary.get("endpoints", {}).items():
            for sec_ep in sec_eps:
                sec_path = sec_ep.get("endpoint", "")
                # For each primary entity, check for a match.
                for primary in data.get("primary_entities", []):
                    primary_name = primary.get("entity_name", "")
                    if not primary_name:
                        continue
                    variations = primary_entity_variations.get(primary_name, {primary_name})
                    # If any variation of the primary entity name is found in the secondary endpoint path,
                    # add the secondary entity to every endpoint (and suggested workflows) of that primary entity.
                    if any(variation in sec_path for variation in variations):
                        endpoints = primary.get("endpoints", {})
                        for m, ep_list in endpoints.items():
                            for ep in ep_list:
                                related = ep.get("related_secondary_entities", [])
                                if sec_name not in related:
                                    related.append(sec_name)
                                ep["related_secondary_entities"] = related
                                if "suggested_workflow" in ep:
                                    for workflow in ep["suggested_workflow"]:
                                        related_wf = workflow.get("related_secondary_entities", [])
                                        if sec_name not in related_wf:
                                            related_wf.append(sec_name)
                                        workflow["related_secondary_entities"] = related_wf

    return data


# ---- Example usage ----

if __name__ == '__main__':
    # Example JSON structure (as provided in your example)
    json_data = {
        "primary_entities": [
            {
                "entity_name": "cyoda_env",
                "endpoints": {
                    "POST": [
                        {
                            "endpoint": "/deploy/cyoda-env",
                            "description": "Create a new cyoda_env.",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    user_name = data.get('user_name')\n    local_cache[user_name] = {'env_config': 'mock_env_config'}\n    response = await mock_teamcity_api('/app/rest/buildQueue', method='POST', json={'user_name': user_name})\n    return jsonify(response), 201\n",
                            "action": "create_env",
                            "suggested_workflow": [
                                {
                                    "start_state": "cyoda_env_not_created",
                                    "end_state": "cyoda_env_created",
                                    "action": "create_env",
                                    "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    user_name = data.get('user_name')\n    local_cache[user_name] = {'env_config': 'mock_env_config'}\n    response = await mock_teamcity_api('/app/rest/buildQueue', method='POST', json={'user_name': user_name})\n    return jsonify(response), 201\n",
                                    "description": "Create a new cyoda_env.",
                                    "related_secondary_entities": []
                                }
                            ]
                        }
                    ],
                    "GET": [
                        {
                            "endpoint": "/cyoda_env/<id>",
                            "description": "Retrieve a cyoda_env by ID.",
                            "complete_code_for_action_derived_from_the_prototype": ""
                        },
                        {
                            "endpoint": "/cyoda_envs",
                            "description": "Retrieve all cyoda_envs entries.",
                            "complete_code_for_action_derived_from_the_prototype": ""
                        }
                    ]
                }
            },
            {
                "entity_name": "user_app",
                "endpoints": {
                    "POST": [
                        {
                            "endpoint": "/deploy/user_app",
                            "description": "Create a new user_app.",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    repository_url = data.get('repository_url')\n    is_public = data.get('is_public')\n    response = await mock_teamcity_api('/app/rest/buildQueue', method='POST', json={'repository_url': repository_url, 'is_public': is_public})\n    return jsonify(response), 201\n",
                            "action": "deploy_app",
                            "suggested_workflow": [
                                {
                                    "start_state": "user_app_not_created",
                                    "end_state": "user_app_created",
                                    "action": "deploy_app",
                                    "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    repository_url = data.get('repository_url')\n    is_public = data.get('is_public')\n    response = await mock_teamcity_api('/app/rest/buildQueue', method='POST', json={'repository_url': repository_url, 'is_public': is_public})\n    return jsonify(response), 201\n",
                                    "description": "Create a new user_app.",
                                    "related_secondary_entities": []
                                }
                            ]
                        }
                    ],
                    "GET": [
                        {
                            "endpoint": "/user_app/<id>",
                            "description": "Retrieve a user_app by ID.",
                            "complete_code_for_action_derived_from_the_prototype": ""
                        },
                        {
                            "endpoint": "/user_apps",
                            "description": "Retrieve all user_apps entries.",
                            "complete_code_for_action_derived_from_the_prototype": ""
                        }
                    ]
                }
            },
            {
                "entity_name": "cancel_user_app",
                "endpoints": {
                    "POST": [
                        {
                            "endpoint": "/deploy/cancel/user_app/<id>",
                            "description": "Create a new cancel_user_app.",
                            "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    comment = data.get('comment')\n    readd_into_queue = data.get('readdIntoQueue')\n    response = await mock_teamcity_api(f'/app/rest/builds/id:{id}', method='POST', json={'comment': comment, 'readdIntoQueue': readd_into_queue})\n    return jsonify({'message': 'Build canceled successfully'}), 200\n",
                            "action": "cancel_user_app",
                            "suggested_workflow": [
                                {
                                    "start_state": "cancel_user_app_not_created",
                                    "end_state": "cancel_user_app_created",
                                    "action": "cancel_user_app",
                                    "complete_code_for_action_derived_from_the_prototype": "\n    data = await request.get_json()\n    comment = data.get('comment')\n    readd_into_queue = data.get('readdIntoQueue')\n    response = await mock_teamcity_api(f'/app/rest/builds/id:{id}', method='POST', json={'comment': comment, 'readdIntoQueue': readd_into_queue})\n    return jsonify({'message': 'Build canceled successfully'}), 200\n",
                                    "description": "Create a new cancel_user_app.",
                                    "related_secondary_entities": []
                                }
                            ]
                        }
                    ],
                    "GET": [
                        {
                            "endpoint": "/cancel_user_app/<id>",
                            "description": "Retrieve a cancel_user_app by ID.",
                            "complete_code_for_action_derived_from_the_prototype": ""
                        },
                        {
                            "endpoint": "/cancel_user_apps",
                            "description": "Retrieve all cancel_user_apps entries.",
                            "complete_code_for_action_derived_from_the_prototype": ""
                        }
                    ]
                }
            }
        ],
        "secondary_entities": [
            {
                "entity_name": "cyoda_env_status",
                "endpoints": {
                    "GET": [
                        {
                            "endpoint": "/deploy/cyoda-env/status/<id>",
                            "description": "Retrieve cyoda_env_status information.",
                            "complete_code_for_action_derived_from_the_prototype": "\n    response = await mock_teamcity_api(f'/app/rest/buildQueue/id:{id}', method='GET')\n    return jsonify(response), 200\n"
                        }
                    ]
                }
            },
            {
                "entity_name": "cyoda_env_statistics",
                "endpoints": {
                    "GET": [
                        {
                            "endpoint": "/deploy/cyoda-env/statistics/<id>",
                            "description": "Retrieve cyoda_env_statistics information.",
                            "complete_code_for_action_derived_from_the_prototype": "\n    response = await mock_teamcity_api(f'/app/rest/builds/id:{id}/statistics/', method='GET')\n    return jsonify(response), 200\n"
                        }
                    ]
                }
            }
        ]
    }

    # Process the JSON data to add related secondary entities.
    updated_json = add_related_secondary_entities(json_data)

    # Print the updated JSON (pretty-printed)
    print(json.dumps(updated_json, indent=4))
