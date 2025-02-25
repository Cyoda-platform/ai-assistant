import re

def extract_entity_names(code: str) -> list:
    """
    Extracts unique entity names from the given Python source code by
    searching for occurrences of entity_model assignments (e.g., entity_model="datum")
    in a case-insensitive manner.

    Parameters:
        code (str): The Python source code as a string.

    Returns:
        list: A list of unique entity names found in the code.
    """
    # Regular expression to capture the entity model name inside quotes, case-insensitively.
    pattern = r'entity_model\s*=\s*["\']([^"\']+)["\']'
    matches = re.findall(pattern, code, flags=re.IGNORECASE)
    return list(set(matches))


# Example usage:
if __name__ == '__main__':

    source_code = """
   #!/usr/bin/env python3

import io
import csv
import aiohttp
from dataclasses import dataclass
from quart import Quart, request, jsonify, Response
from quart_schema import QuartSchema, validate_querystring

# Import external service functions and supporting variables.
from common.config.config import ENTITY_VERSION
from common.repository.cyoda.cyoda_init import init_cyoda
from app_init.app_init import cyoda_token

ENTITY_MODEL = "companies_jobs"  # Entity model name used in entity_service calls

app = Quart(__name__)
# Initialize Quart Schema for request/response validation
QuartSchema(app)

# Initialize cyoda before serving.
@app.before_serving
async def startup():
    await init_cyoda(cyoda_token)
    await ingest_data()  # Ingest data from external source at startup

# Local in-memory cache for companies
companies_cache = []

async def ingest_data():

    # Simulated URL for external data source
    external_api_url = "http://external-data-source.com/companies"  # Placeholder URL

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(external_api_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for company in data:
                        # Assuming the external data source returns a list of company dictionaries
                        companies_cache.append({
                            "companyName": company.get("companyName"),
                            "businessId": company.get("businessId"),
                            "companyType": company.get("companyType"),
                            "registrationDate": company.get("registrationDate"),
                            "status": company.get("status"),
                            "lei": company.get("lei", None),
                        })
                else:
                    print(f"Failed to fetch data: {resp.status}")
        except Exception as e:
            print(f"Error fetching data: {e}")

# Define dataclasses for querystring validation.
@dataclass
class CompaniesQuery:
    name: str = None
    location: str = None
    businessId: str = None
    companyForm: str = None
    format: str = "json"  # Default output format is JSON

@dataclass
class LeiQuery:
    businessId: str  # businessId is required for LEI lookup

# GET /companies endpoint.
@validate_querystring(CompaniesQuery)  # This decorator validates querystring parameters before route handling.
@app.route("/companies", methods=["GET"])
async def get_companies():

    # Retrieve query parameters.
    name = request.args.get("name")
    location = request.args.get("location")
    business_id = request.args.get("businessId")
    company_form = request.args.get("companyForm")
    output_format = (request.args.get("format") or "json").lower()

    # Filter companies based on search criteria from the in-memory cache.
    filtered_companies = []
    for comp in companies_cache:
        # Only include active companies.
        if (comp.get("status") or "").lower() != "active":
            continue
        if name and name.lower() not in (comp.get("companyName") or "").lower():
            continue
        if location and location.lower() not in (comp.get("location") or "").lower():
            continue
        if business_id and business_id != comp.get("businessId"):
            continue
        if company_form and company_form.lower() not in (comp.get("companyType") or "").lower():
            continue

        # For companies without LEI, mark as "Not Available"
        comp_copy = comp.copy()
        if not comp_copy.get("lei"):
            comp_copy["lei"] = "Not Available"
        filtered_companies.append(comp_copy)

    if not filtered_companies:
        return jsonify({"error": "No companies found"}), 404

    # Return results in the selected output format.
    if output_format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=filtered_companies[0].keys())
        writer.writeheader()
        for comp in filtered_companies:
            writer.writerow(comp)
            entity_model="test"
        return Response(output.getvalue(), mimetype="text/csv")
    else:
        return jsonify({"companies": filtered_companies})

# GET /companies/lei endpoint.
@validate_querystring(LeiQuery)  # Validates that businessId is provided and is a string.
@app.route("/companies/lei", methods=["GET"])
async def get_company_lei():

    business_id = request.args.get("businessId")
    if not business_id:
        return jsonify({"error": "Missing businessId parameter"}), 400

    # Retrieve the company using the provided businessId from the local cache.
    company = next((c for c in companies_cache if c.get("businessId") == business_id), None)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    lei_value = company.get("lei")
    if lei_value:
        return jsonify({"lei": lei_value})
    else:
        # No LEI available in the record; perform external lookup.
        external_api_url = f"http://external-lei-api.com/lookup?businessId={business_id}"  # Placeholder URL.
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(external_api_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        lei = data.get("lei", "Not Available")
                        # Update the company record with the new LEI.
                        company["lei"] = lei
                        return jsonify({"lei": lei})
                    else:
                        return jsonify({"lei": "Not Available"}), 200
            except Exception as e:
                # TODO: Log the exception properly.
                return jsonify({"lei": "Not Available"}), 200

if __name__ == '__main__':
    # Run the Quart application.
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)

    """

    entity_names = extract_entity_names(source_code)
    print("Entity Names Found:", entity_names)