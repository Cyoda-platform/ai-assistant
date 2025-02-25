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


# NEW: Transformer to remove the workflow argument from entity_service.add_item calls.
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
    # NEW: Remove workflow arguments from entity_service.add_item calls.
    new_module = new_module.visit(RemoveWorkflowArgument())
    code_without_workflow = new_module.code

    # Helper: extract the source for a node.
    def get_source_for_node(node: cst.CSTNode) -> str:
        pos = metadata[node]
        lines = source_code.splitlines(keepends=True)
        start_index = sum(len(lines[i]) for i in range(pos.start.line - 1)) + pos.start.column
        end_index = sum(len(lines[i]) for i in range(pos.end.line - 1)) + pos.end.column
        return source_code[start_index:end_index]

    # Build JSON mapping for each entity_model.
    json_output = []
    for entity, deps in entity_to_deps.items():
        func_nodes = [functions[name] for name in deps if name in functions]
        func_nodes.sort(key=lambda x: x[1])
        combined_source = "\n".join(get_source_for_node(node) for node, _ in func_nodes)
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
import asyncio
import datetime
import json
from dataclasses import dataclass

from quart import Quart, request, jsonify, abort
from quart_schema import QuartSchema, validate_request, validate_response  # For POST, route decorator comes first, then validators.
import aiohttp

from common.config.config import ENTITY_VERSION  # Use this constant for all entity_service calls
from app_init.app_init import cyoda_token, entity_service
from common.repository.cyoda.cyoda_init import init_cyoda

app = Quart(__name__)
QuartSchema(app)  # Initialize QuartSchema

# Define entity model name for the search jobs
ENTITY_MODEL = "company_search_job"

# Data validation models
@dataclass
class SearchRequest:
    companyName: str
    # Optional filters field if needed
    filters: dict = None  # default to None if not provided

@dataclass
class SearchResponse:
    searchId: str
    status: str
    requestedAt: str

# Constants for external API endpoints
FINNISH_API_URL = "https://avoindata.prh.fi/opendata-ytj-api/v3/companies"
LEI_API_URL = "https://example.com/lei-lookup"  # Placeholder URL

async def fetch_companies(session: aiohttp.ClientSession, company_name: str, filters: dict):
    # Construct query parameters: currently using only companyName
    params = {"name": company_name}
    # If any filters are provided, add them to the params (prevent accidental None)
    if filters:
        params.update(filters)
    try:
        async with session.get(FINNISH_API_URL, params=params, timeout=10) as resp:
            if resp.status != 200:
                # In case of non-200, return empty list (or consider raising exception)
                return []
            data = await resp.json()
            # Assume the response data has a "results" key; adjust accordingly if needed.
            return data.get("results", [])
    except Exception:
        return []

async def fetch_lei(session: aiohttp.ClientSession, company: dict):
    # This is a placeholder implementation that simulates a network call.
    try:
        # Simulate network delay
        await asyncio.sleep(0.5)
        # Dummy logic for demonstration: if company name contains "Acme", return a dummy LEI.
        if "Acme" in company.get("companyName", ""):
            return "529900T8BM49AURSDO55"
    except Exception:
        pass
    return "Not Available"

# Workflow function that processes the search job entity before it is persisted.
# All asynchronous tasks (like fetching companies and LEI) are handled here,
# freeing the controller from any excessive logic.
async def process_company_search_job(entity: dict):
    # This workflow function runs before persistence and updates the entity in memory.
    async with aiohttp.ClientSession() as session:
        try:
            payload = entity.get("payload", {})
            company_name = payload.get("companyName")
            if not company_name:
                raise ValueError("Missing companyName in payload")
            filters = payload.get("filters", {}) or {}
            companies = await fetch_companies(session, company_name, filters)
            # Filter companies: example filtering for those with "active" status.
            active_companies = [c for c in companies if c.get("status", "").lower() == "active"]
            enriched_results = []
            for company in active_companies:
                lei = await fetch_lei(session, company)
                enriched = {
                    "companyName": company.get("companyName", "Unknown"),
                    "businessId": company.get("businessId", "Unknown"),
                    "companyType": company.get("companyType", "Unknown"),
                    "registrationDate": company.get("registrationDate", "Unknown"),
                    "status": "Active",
                    "LEI": lei,
                }
                enriched_results.append(enriched)
            # Update the entity state; do not call any external entity service functions!
            entity["status"] = "success"
            entity["results"] = enriched_results
            entity["completedAt"] = datetime.datetime.utcnow().isoformat()
        except Exception as e:
            entity["status"] = "failure"
            entity["error"] = str(e)
    # Return the in-memory modified entity which will be persisted.
    return entity

@app.route('/api/companies/search', methods=['POST'])
@validate_request(SearchRequest)  # Validation on input data.
@validate_response(SearchResponse, 202)
async def search_companies(data: SearchRequest):
    # Capture the timestamp when the request was received.
    requested_at = datetime.datetime.utcnow().isoformat()
    # Prepare the search job data including the payload received from the client.
    job_data = {
        "status": "processing",
        "requestedAt": requested_at,
        "payload": data.__dict__
    }
    # Use the external service to add a new search job.
    # The workflow function process_company_search_job is applied asynchronously
    # before the entity is persisted, handling all required asynchronous tasks.
    job_id = await entity_service.add_item(
        token=cyoda_token,
        entity_model=ENTITY_MODEL,
        entity_version=ENTITY_VERSION,  # always use this constant
        entity=job_data,  # job data including search parameters
        workflow=process_company_search_job  # Workflow applied asynchronously before persistence.
    )
    return jsonify({"searchId": job_id, "status": "processing", "requestedAt": requested_at}), 202

@app.route('/api/companies/results/<job_id>', methods=['GET'])
async def get_search_results(job_id: str):
    # Retrieve job details via the external service.
    job = await entity_service.get_item(
        token=cyoda_token,
        entity_model=ENTITY_MODEL,
        entity_version=ENTITY_VERSION,
        technical_id=job_id
    )
    if not job:
        abort(404, description="Job not found")
    # Return appropriate response based on job status.
    if job.get("status") == "processing":
        return jsonify({"searchId": job_id, "status": "processing"}), 202
    elif job.get("status") == "failure":
        return jsonify({
            "searchId": job_id,
            "status": "failure",
            "error": job.get("error", "Unknown error")
        }), 500
    else:
        return jsonify({
            "searchId": job_id,
            "status": "success",
            "results": job.get("results", [])
        }), 200

@app.route('/api/companies/results', methods=['GET'])
async def list_search_jobs():
    # Retrieve a list of all search jobs via the external service.
    jobs_list = await entity_service.get_items(
        token=cyoda_token,
        entity_model=ENTITY_MODEL,
        entity_version=ENTITY_VERSION,
    )
    return jsonify(jobs_list), 200

@app.before_serving
async def startup():
    # Initialize external cyoda repository before serving.
    await init_cyoda(cyoda_token)

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
    '''
    code_without, workflow_json = analyze_code_with_libcst(input_code)
    print("----- Code without workflow functions -----")
    print(code_without)
    print("----- Extracted Workflow Functions (JSON) -----")
    print(json.dumps(workflow_json, indent=2))
