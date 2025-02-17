import re


def validate_code_by_text(code, schema, entity_name):
    """
    Validates the given code string using regex scanning according to the following rules:

      1. The code must include these imports:
            import json
            import logging
            from app_init.app_init import entity_service
            from common.config.config import ENTITY_VERSION

      2. Every async function that is not listed as an action in the schema (supplementary)
         must have a name that starts with an underscore.

      3. Every async function that is an action (i.e. listed in the schema) must be present in the code
         with a header of the form:
            async def <action_name>(<parameters>):
         and must have exactly two parameters: data, meta.

      4. For each action function that has related secondary entities (per schema), its body must contain
         at least one uncommented line calling entity_service.add_item or entity_service.get_item
         with that entity name provided as a literal (i.e. quoted).

      5. When scanning the entire code (excluding commented lines) for calls to entity_service.add_item or
         get_item where the second parameter is not a literal (i.e. does not start with a quote),
         an error is reported only if that second parameter contains the substring given by entity_name.

    Returns:
        A list of error messages found during validation.
    """
    errors = []

    # --- 1. Validate required imports ---
    required_imports = [
        "import json",
        "import logging",
        "from app_init.app_init import entity_service",
        "from common.config.config import ENTITY_VERSION"
    ]
    for imp in required_imports:
        if imp not in code:
            errors.append(f"Missing required import: {imp}")

    # --- 2. Find all async function definitions ---
    # This regex finds function headers and captures the function name and its parameter list.
    func_pattern = re.compile(r'async\s+def\s+(\w+)\s*\((.*?)\)\s*:', re.DOTALL)
    funcs = []
    for match in func_pattern.finditer(code):
        name = match.group(1)
        params = match.group(2)
        start_index = match.start()
        end_index = match.end()
        funcs.append({
            "name": name,
            "params": params,
            "start": start_index,
            "end": end_index
        })

    # --- 3. Determine expected action functions from the schema ---
    expected_actions = set()
    action_secondary = {}
    for step in schema.get("suggested_workflow", []):
        action = step.get("action")
        if action:
            expected_actions.add(action)
            action_secondary[action] = step.get("related_secondary_entities", [])

    # --- 4. Validate function definitions ---
    funcs_by_name = {f["name"]: f for f in funcs}

    # 4a. Check that every expected action function is present.
    for action in expected_actions:
        if action not in funcs_by_name:
            errors.append(f"Action function '{action}' is missing.")

    # 4b. Iterate over every async function found.
    for func in funcs:
        name = func["name"]
        params = func["params"]

        if name in expected_actions:
            # Validate that action functions have exactly two parameters: data, meta.
            params_list = [p.strip() for p in params.split(",") if p.strip()]
            # Strip any default values.
            param_names = [p.split("=")[0].strip() for p in params_list]
            if param_names != ["data", "meta"]:
                errors.append(
                    f"Action function '{name}' must have exactly two parameters: data, meta. Found: {param_names}")

            # If the action has related secondary entities, check for uncommented code that calls add_item or get_item.
            secondary_entities = action_secondary.get(name, [])
            if secondary_entities:
                # Determine the function body: code from the end of the header until the next async def or EOF.
                body_start = func["end"]
                next_match = func_pattern.search(code, pos=body_start)
                if next_match:
                    body = code[body_start:next_match.start()]
                else:
                    body = code[body_start:]
                for entity in secondary_entities:
                    # Look for an uncommented line that calls add_item or get_item with the entity name as a literal.
                    pattern = re.compile(
                        rf'^(?!\s*#).*entity_service\.(add_item|get_item)\(.*[\'"]{re.escape(entity)}[\'"].*\)',
                        re.MULTILINE
                    )
                    if not pattern.search(body):
                        errors.append(
                            f"Action function '{name}' is missing uncommented code to save or retrieve secondary entity '{entity}'."
                        )
        else:
            # Supplementary functions must start with an underscore.
            if not name.startswith("_"):
                errors.append(f"Supplementary function '{name}' must start with an underscore.")

    # --- 5. Additional check for disallowed variable entity names ---
    # Search the entire code (excluding commented lines) for calls to entity_service.add_item or get_item
    # where the second parameter is not a literal (i.e. does not start with a quote) and it contains the substring entity_name.
    pattern_var = re.compile(
        r'^(?!\s*#).*entity_service\.(add_item|get_item)\(\s*meta\[\s*[\'"]token[\'"]\s*\]\s*,\s*([^\'"][^,\)]*)',
        re.MULTILINE
    )
    for match in pattern_var.finditer(code):
        method = match.group(1)
        second_arg = match.group(2).strip()
        if entity_name in second_arg:
            errors.append(
                f"{method} should not be used to directly save/access current *this* entity {second_arg}.  Please use data argument instead"
            )

    return errors


# =====================================
# Example usage:
# =====================================
if __name__ == "__main__":
    # Sample code string to validate.
    sample_code = '''
import json
import logging
from app_init.app_init import entity_service
from common.config.config import ENTITY_VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _fetch_bitcoin_rates():
    await asyncio.sleep(0.1)
    return {"BTC": 50000}

async def _send_email(report_id, rates, email):
    logger.info(f"Sending report {report_id} to {email} with rates: {rates}")
    await asyncio.sleep(0.1)

async def create_report(data: "cyoda_token"}):
    """Initiates the report creation process and sends an email."""
    try:
        data = await request.get_json()
        email = data.get('email')
        report_id = str(uuid.uuid4())
        rates = await _fetch_bitcoin_rates()
        asyncio.create_task(_send_email(report_id, rates, email))
        reports[report_id] = {...}
        # Correct call: literal entity name.
        #result = await entity_service.add_item(meta['token'], 'report', ENTITY_VERSION, data)
        return jsonify({...}), 202
    except Exception as e:
        logger.error(f"Error in send_teamcity_request: {e}")
        raise

async def create_report_with_var(data, meta={"token": "cyoda_token"}):
    """Action with variable entity name usage (should trigger an error)."""
    try:
        data = await request.get_json()
        email = data.get('email')
        report_id = str(uuid.uuid4())
        rates = await _fetch_bitcoin_rates()
        asyncio.create_task(_send_email(report_id, rates, email))
        reports[report_id] = {...}
        # Incorrect call: variable is used for entity name.
        result = await entity_service.add_item(meta['token'], job, ENTITY_VERSION, data)
        return jsonify({...}), 202
    except Exception as e:
        logger.error(f"Error in create_report_with_var: {e}")
        raise

async def extra_helper(param):
    # This supplementary function does not start with an underscore.
    pass
'''

    # Sample schema corresponding to the intended workflow.
    sample_schema = {
        "suggested_workflow": [
            {
                "action": "create_report",
                "description": "Initiates the report creation process and sends an email.",
                "complete_code_for_action_derived_from_the_prototype": "",
                "related_secondary_entities": ["report"]
            },
            {
                "action": "create_report_with_var",
                "description": "Action with variable entity name usage.",
                "complete_code_for_action_derived_from_the_prototype": "",
                "related_secondary_entities": ["report"]
            }
        ]
    }

    # Run validation and collect errors.
    error_list = validate_code_by_text(sample_code, sample_schema, "job")

    # Print the list of errors.
    print("Validation Errors:")
    for err in error_list:
        print(" -", err)
