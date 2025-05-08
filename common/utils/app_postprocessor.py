import re

def app_post_process(text: str) -> str:
    lines = text.splitlines(keepends=True)
    start_index = None
    startup_index = None
    await_index = None
    indent = ""

    # Locate the @app.before_serving line.
    for i, line in enumerate(lines):
        if "@app.before_serving" in line:
            start_index = i
            indent = re.match(r"^(\s*)", line).group(1)
            break
    if start_index is None:
        # If the decorator isn’t found, return text unchanged.
        return text

    # Find the startup function definition line after the decorator.
    for i in range(start_index + 1, len(lines)):
        # Check after stripping left-side spaces.
        if lines[i].lstrip().startswith("async def startup("):
            startup_index = i
            break
    if startup_index is None:
        return text

    # Find the line with the awaited call in the startup function.
    for i in range(startup_index + 1, len(lines)):
        if "await init_cyoda(cyoda_token)" in lines[i]:
            await_index = i
            break
    if await_index is None:
        return text

    # Build the replacement block, preserving the original indentation.
    replacement_block = (
        f"{indent}@app.before_serving\n"
        f"{indent}async def startup():\n"
        f"{indent}    await init_cyoda(cyoda_token)\n"
        f"{indent}    app.background_task = asyncio.create_task(grpc_stream(cyoda_token))\n\n"
        f"{indent}@app.after_serving\n"
        f"{indent}async def shutdown():\n"
        f"{indent}    app.background_task.cancel()\n"
        f"{indent}    await app.background_task\n"
    )

    # Replace from the start of the decorator up through the awaited call line.
    new_lines = lines[:start_index] + [replacement_block] + lines[await_index + 1:]

    # Ensure the grpc_stream import is added.
    import_line = "from common.grpc_client.grpc_client import grpc_stream\n"
    replaced = False
    for i, line in enumerate(new_lines):
        if "#!/usr/bin/env python3" in line:
            new_lines[i] = import_line
            replaced = True
            break
    if not replaced:
        new_lines.insert(0, import_line)

    return "".join(new_lines)


# Example usage:
if __name__ == "__main__":
    sample_code = """
import asyncio
import aiohttp
import uuid
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

from quart import Quart, request, jsonify, abort
from quart_schema import QuartSchema, validate_request, validate_response

from common.config.config import ENTITY_VERSION
from app_init.app_init import entity_service, cyoda_token
from common.repository.cyoda.cyoda_init import init_cyoda

app = Quart(__name__)
QuartSchema(app)

# Initialize external services before serving requests.
@app.before_serving
async def startup():



    await init_cyoda(cyoda_token)

# External API endpoints (placeholders, adjust if needed)
PRH_API_URL = "https://avoindata.prh.fi/opendata-ytj-api/v3/companies"
LEI_API_URL = "https://example.com/lei"  # TODO: Replace with an official LEI registry endpoint.

# Dataclass for validating POST request payload for company search.
@dataclass
class CompanySearch:
    companyName: str
    location: Optional[str] = None
    businessId: Optional[str] = None
    companyForm: Optional[str] = None
    registrationDateStart: Optional[str] = None
    registrationDateEnd: Optional[str] = None

# Dataclass for validating POST response.
@dataclass
class SearchResponse:
    searchId: str
    message: str

# POST endpoint for initiating a company search.
# The controller logic is slim, handing over processing to the workflow function.
@app.route("/api/companies/search", methods=["POST"])
@validate_request(CompanySearch)
@validate_response(SearchResponse, 202)
async def search_companies(data: CompanySearch):
    if not data.companyName:
        return jsonify({"error": "companyName is required"}), 400

    # Generate a unique search ID and record the timestamp.
    search_id = str(uuid.uuid4())
    requested_at = datetime.utcnow().isoformat() + "Z"
    # Include search criteria in the persisted entity so the workflow can use them.
    job_data = {
        "id": search_id,
        "status": "processing",
        "requestedAt": requested_at,
        "result": None,
        "criteria": asdict(data)
    }
    # Persist the entity using the add_item method with workflow processing.
    # The workflow function process_search_job will be invoked asynchronously before persistence.
    entity_service.add_item(
        token=cyoda_token,
        entity_model="search_job",
        entity_version=ENTITY_VERSION,  # always use this constant
        entity=job_data,
        )
    # Return initial response with searchId.
    return SearchResponse(searchId=search_id, message="Processing started"), 202

# GET endpoint for retrieving search results.
@app.route("/api/companies/<search_id>", methods=["GET"])
async def get_search_result(search_id):
    job = entity_service.get_item(
        token=cyoda_token,
        entity_model="search_job",
        entity_version=ENTITY_VERSION,
        technical_id=search_id
    )
    if not job:
        abort(404, description="Search ID not found")
    if job.get("status") == "processing":
        return jsonify({"status": "processing", "message": "Results are not ready yet. Please try again later."}), 202
    elif job.get("status") == "failed":
        return jsonify({"status": "failed", "error": job.get("error", "Unknown error occurred")}), 500
    return jsonify(job.get("result")), 200



if __name__ == '__main__':
    # Run the application with debug and threaded mode settings.
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
"""
    new_code = app_post_process(sample_code)
    print(new_code)
