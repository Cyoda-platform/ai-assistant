import json

import libcst as cst
from libcst.metadata import PositionProvider, MetadataWrapper


# Visitor to collect all top-level function definitions.
class FunctionDefCollector(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self):
        # Mapping: function name -> (node, start_line)
        self.functions = {}

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        pos = self.get_metadata(PositionProvider, node)
        self.functions[node.name.value] = (node, pos.start.line)


# Visitor to collect global constant assignments for simple string literals.
class GlobalConstantCollector(cst.CSTVisitor):
    def __init__(self):
        # Mapping: variable name -> constant string value
        self.constants = {}

    def visit_Assign(self, node: cst.Assign) -> None:
        # Only process assignments with one target that is a simple name.
        if len(node.targets) == 1 and isinstance(node.targets[0].target, cst.Name):
            target_name = node.targets[0].target.value
            if isinstance(node.value, cst.SimpleString):
                # Strip quotes from the string literal.
                self.constants[target_name] = node.value.value.strip('"').strip("'")


# Visitor to collect entity_service.add_item calls and extract entity_model and workflow.
class AddItemCallCollector(cst.CSTVisitor):
    def __init__(self, constants):
        # Mapping: entity_model -> workflow function name
        self.mapping = {}
        self.constants = constants

    def visit_Call(self, node: cst.Call) -> None:
        # Look for calls to entity_service.add_item
        if isinstance(node.func, cst.Attribute):
            if (
                isinstance(node.func.value, cst.Name)
                and node.func.value.value == "entity_service"
                and node.func.attr.value == "add_item"
            ):
                entity_model_val = None
                workflow_val = None
                for arg in node.args:
                    if arg.keyword:
                        if arg.keyword.value == "entity_model":
                            # If the value is a string literal, use it.
                            if isinstance(arg.value, cst.SimpleString):
                                entity_model_val = arg.value.value.strip('"').strip("'")
                            # Otherwise if it's a name, try to look it up in the constants.
                            elif isinstance(arg.value, cst.Name):
                                entity_model_val = self.constants.get(arg.value.value)
                        elif arg.keyword.value == "workflow":
                            if isinstance(arg.value, cst.Name):
                                workflow_val = arg.value.value
                if entity_model_val and workflow_val:
                    self.mapping[entity_model_val] = workflow_val


# Recursively collect function dependencies starting from a given function.
def get_dependencies(fn_name, functions):
    deps = set()
    to_process = {fn_name}
    while to_process:
        current = to_process.pop()
        if current in functions:
            node, _ = functions[current]

            class CalledFuncCollector(cst.CSTVisitor):
                def __init__(self):
                    self.called = set()

                def visit_Call(self, call_node: cst.Call):
                    if isinstance(call_node.func, cst.Name):
                        self.called.add(call_node.func.value)

            collector = CalledFuncCollector()
            node.visit(collector)
            for called in collector.called:
                if called in functions and called not in deps:
                    deps.add(called)
                    to_process.add(called)
    deps.add(fn_name)
    return deps


# Transformer to remove functions whose names are in names_to_remove.
class RemoveWorkflowFunctions(cst.CSTTransformer):
    def __init__(self, names_to_remove):
        self.names_to_remove = names_to_remove

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef):
        if original_node.name.value in self.names_to_remove:
            return cst.RemoveFromParent()
        return updated_node


# Transformer to remove the workflow argument from entity_service.add_item calls.
class RemoveWorkflowArgument(cst.CSTTransformer):
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.CSTNode:
        if isinstance(updated_node.func, cst.Attribute):
            if (
                isinstance(updated_node.func.value, cst.Name)
                and updated_node.func.value.value == "entity_service"
                and updated_node.func.attr.value == "add_item"
            ):
                new_args = []
                for arg in updated_node.args:
                    if arg.keyword and arg.keyword.value == "workflow":
                        # Remove the argument if its value is a name starting with "process_".
                        if isinstance(arg.value, cst.Name) and arg.value.value.startswith("process_"):
                            continue
                    new_args.append(arg)
                return updated_node.with_changes(args=new_args)
        return updated_node


def analyze_code_with_libcst(source_code: str):
    # Parse the module and wrap with metadata.
    module = cst.parse_module(source_code)
    wrapper = MetadataWrapper(module)
    metadata = wrapper.resolve(PositionProvider)

    # Extract top-level import statements and constant assignments.
    header_nodes = []
    for stmt in module.body:
        if isinstance(stmt, cst.SimpleStatementLine):
            for small_stmt in stmt.body:
                if isinstance(small_stmt, (cst.Import, cst.ImportFrom)):
                    header_nodes.append(stmt)
                    break
                elif isinstance(small_stmt, cst.Assign):
                    # Only include simple string constant assignments.
                    if (
                        len(small_stmt.targets) == 1
                        and isinstance(small_stmt.targets[0].target, cst.Name)
                        and isinstance(small_stmt.value, cst.SimpleString)
                    ):
                        header_nodes.append(stmt)
                        break

    def get_source_for_node(node: cst.CSTNode) -> str:
        try:
            pos = metadata[node]
            lines = source_code.splitlines(keepends=True)
            start_index = sum(len(lines[i]) for i in range(pos.start.line - 1)) + pos.start.column
            end_index = sum(len(lines[i]) for i in range(pos.end.line - 1)) + pos.end.column
            return source_code[start_index:end_index]
        except KeyError:
            # Fallback: wrap node in a Module and return its generated code.
            return cst.Module(body=[node]).code

    header_code = "\n".join(get_source_for_node(node) for node in header_nodes)

    # Collect global constants.
    constant_collector = GlobalConstantCollector()
    wrapper.visit(constant_collector)
    constants = constant_collector.constants

    # Collect all top-level function definitions.
    func_collector = FunctionDefCollector()
    wrapper.visit(func_collector)
    functions = func_collector.functions

    # Collect mapping from entity_model to workflow function name.
    additem_collector = AddItemCallCollector(constants)
    wrapper.visit(additem_collector)
    entity_workflow_map = additem_collector.mapping

    # For each workflow function, recursively collect dependencies.
    entity_to_deps = {}
    all_deps = set()
    for entity, wf_name in entity_workflow_map.items():
        deps = get_dependencies(wf_name, functions)
        entity_to_deps[entity] = deps
        all_deps |= deps

    # Remove workflow functions (and their dependencies) from the original module.
    transformer = RemoveWorkflowFunctions(all_deps)
    new_module = wrapper.module.visit(transformer)
    # Remove workflow arguments from entity_service.add_item calls.
    new_module = new_module.visit(RemoveWorkflowArgument())
    code_without_workflow = new_module.code

    # Build JSON mapping for each entity_model.
    json_output = []
    for entity, deps in entity_to_deps.items():
        func_nodes = [functions[name] for name in deps if name in functions]
        func_nodes.sort(key=lambda x: x[1])
        # Prepend header (imports and constants) to the extracted workflow code.
        combined_source = header_code + "\n" + "\n".join(get_source_for_node(node) for node, _ in func_nodes)
        json_output.append({
            entity: {
                "workflow_function": entity_workflow_map.get(entity),
                "code": combined_source
            }
        })

    return code_without_workflow, json_output


# Example usage:
if __name__ == "__main__":
    input_code = r'''
#!/usr/bin/env python3
"""
Prototype implementation for a Quart API that fetches and displays brand data.
This version replaces all in‐memory cache interactions with calls to the external
entity_service. Data is stored via add_item and later retrieved via get_items.
"""

import asyncio
import datetime
from dataclasses import dataclass
from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request  # noqa: E402
import aiohttp

from common.repository.cyoda.cyoda_init import init_cyoda
from app_init.app_init import cyoda_token, entity_service
from common.config.config import ENTITY_VERSION

app = Quart(__name__)
QuartSchema(app)  # Initialize QuartSchema

# Data class for POST /brands request validation.
@dataclass
class BrandRequest:
    refresh: bool = False

@app.before_serving
async def startup():
    try:
        await init_cyoda(cyoda_token)
    except Exception as e:
        # Log the error and prevent startup if initialization fails.
        print(f"Initialization error: {str(e)}")
        raise

# Asynchronous function to fetch supplementary data.
async def fetch_supplementary_data():
    supplementary_url = "https://api.practicesoftwaretesting.com/brands/supplementary"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(supplementary_url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    # Log failure and return empty dict if non-200 response.
                    print(f"Supplementary data fetch failed with status {resp.status}")
                    return {}
    except Exception as e:
        # Log the exception and return empty dict to avoid breaking the workflow.
        print(f"Supplementary data fetch exception: {str(e)}")
        return {}

# Fire-and-forget async task for logging processing details.
async def log_processing(entity_model, entity_id):
    try:
        # Simulate asynchronous logging (this could be replaced with real logging).
        await asyncio.sleep(0)
        print(f"Processed entity for model '{entity_model}' with id '{entity_id}'")
    except Exception as e:
        # Capture any exceptions in logging to prevent it from affecting the workflow.
        print(f"Logging exception: {str(e)}")

# Workflow function applied to the brand entity before persistence.
async def process_brands(entity_data):
    try:
        # Add a processed timestamp and flag to the entity data.
        entity_data["processed_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        entity_data["is_processed"] = True

        # Fetch supplementary data asynchronously and update the entity.
        supplementary = await fetch_supplementary_data()
        if supplementary:
            entity_data["supplementary_info"] = supplementary

        # Fire-and-forget asynchronous logging.
        entity_id = entity_data.get("id", "unknown")
        asyncio.create_task(log_processing("brands", entity_id))

        # Additional asynchronous tasks (if any) can be added here.
    except Exception as e:
        # If any error occurs during processing, log it.
        print(f"Workflow processing error: {str(e)}")
    return entity_data

# POST /brands endpoint.
@app.route("/brands", methods=["POST"])
@validate_request(BrandRequest)
async def post_brands(data: BrandRequest):
    """
    POST /brands
    Retrieves brand data from an external API and stores it via the external entity_service.
    If refresh is False, it first checks if data already exists.
    """
    refresh = data.refresh

    if not refresh:
        try:
            # Check if brand data already exists in the external service.
            existing_data = await entity_service.get_items(
                token=cyoda_token,
                entity_model="brands",
                entity_version=ENTITY_VERSION,
            )
            if existing_data:
                return jsonify({
                    "success": True,
                    "message": "Brand data already processed and available.",
                    "data": existing_data,
                })
        except Exception as e:
            # Log and continue to fetch fresh data if checking fails.
            print(f"Error retrieving existing data: {str(e)}")

    # External API endpoint for brand data.
    external_api_url = "https://api.practicesoftwaretesting.com/brands"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(external_api_url, timeout=10) as resp:
                if resp.status == 200:
                    external_data = await resp.json()
                else:
                    return jsonify({"success": False, "error": f"External API responded with status {resp.status}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    try:
        # Store the data asynchronously using the external entity_service and apply the workflow.
        # The workflow function process_brands will be invoked asynchronously to transform
        # the entity before its persistence.
        job_id = await entity_service.add_item(
            token=cyoda_token,
            entity_model="brands",
            entity_version=ENTITY_VERSION,  # always use this constant
            entity=external_data,  # the validated data object
            workflow=process_brands  # Workflow function applied to the entity
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"Error storing data: {str(e)}"}), 500

    return jsonify({
         "success": True,
         "message": "Processing initiated.",
         "jobId": job_id
    })

# GET /brands endpoint.
@app.route("/brands", methods=["GET"])
async def get_brands():
    """
    GET /brands
    Returns the processed/stored brand data retrieved via the external entity_service.
    """
    try:
        brands_data = await entity_service.get_items(
            token=cyoda_token,
            entity_model="brands",
            entity_version=ENTITY_VERSION,
        )
    except Exception as e:
        return jsonify({"success": False, "error": f"Error retrieving brand data: {str(e)}"}), 500

    if not brands_data:
         return jsonify({"success": False, "error": "No brand data available. Initiate processing via POST."}), 404

    return jsonify(brands_data)

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
    '''
    code_without, workflow_json = analyze_code_with_libcst(input_code)
    print("----- Code without workflow functions -----")
    print(code_without)
    print("----- Extracted Workflow Functions (JSON) -----")
    print(json.dumps(workflow_json, indent=2))
