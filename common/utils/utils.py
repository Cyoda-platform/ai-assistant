import asyncio
import logging
import os
import queue
import jwt
import time
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import aiofiles
from typing import Optional, Any, Set
import uuid
import json

import httpx
import jsonschema
from jsonschema import validate

from common.auth.cyoda_auth import CyodaAuthService
from common.config.config import config
from common.exception.exceptions import InvalidTokenException

logger = logging.getLogger(__name__)


class ValidationErrorException(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def get_user_history_answer(response):
    answer = response.get('message', '') if response and isinstance(response, dict) else ''
    if isinstance(answer, dict) or isinstance(answer, list):
        answer = json.dumps(answer)
    return answer


def generate_uuid() -> uuid:
    return uuid.uuid1()


def _normalize_boolean_json(json_data):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, str):
                if (value in ["'true'", "'True'", 'True', "true", "True"]):
                    json_data[key] = True
                elif (value in ["'false'", "'False'", 'False', "false", "False"]):
                    json_data[key] = False
            elif isinstance(value, dict):
                json_data[key] = _normalize_boolean_json(value)
    return json_data


def remove_js_style_comments_outside_strings(code: str) -> str:
    """
    Remove //... comments ONLY if they appear outside of a quoted string.

    This prevents 'https://...' in a JSON string from being mistaken as a comment.
    """

    result = []
    in_string = False
    escape_char = False
    i = 0
    length = len(code)

    while i < length:
        char = code[i]

        # Check for string toggle (double quotes only for JSON)
        if char == '"' and not escape_char:
            # Toggle string on/off
            in_string = not in_string
            result.append(char)
        elif not in_string:
            # We are outside a string, so check if we have //
            if char == '/' and i + 1 < length and code[i + 1] == '/':
                # Skip rest of the line
                # Move i to the next newline or end of text
                i += 2
                while i < length and code[i] not in ('\n', '\r'):
                    i += 1
                # Do NOT append the '//...' to result
                # We effectively remove it
                continue
            else:
                # Normal character outside string
                result.append(char)
        else:
            # Inside a string
            result.append(char)

        # Handle escape chars inside strings
        if char == '\\' and in_string and not escape_char:
            # Next character is escaped
            escape_char = True
        else:
            escape_char = False

        i += 1

    return ''.join(result)


def parse_json(text: str) -> str:
    """
    1. Find the first occurrence of '{' or '[' and the matching last occurrence
       of '}' or ']', respectively (very naive bracket slicing).
    2. Remove only real JS-style comments (// ...) outside of strings.
    3. Attempt to parse the substring as JSON.
    4. Return prettified JSON if successful, otherwise the original text.
    """

    original_text = text
    text = text.strip()

    # Find earliest occurrences
    first_curly = text.find('{')
    first_square = text.find('[')

    if first_curly == -1 and first_square == -1:
        # No bracket found
        return original_text

    # Decide which bracket to use based on which occurs first
    if first_curly == -1:
        start_index = first_square
        close_bracket = ']'
    elif first_square == -1:
        start_index = first_curly
        close_bracket = '}'
    else:
        if first_curly < first_square:
            start_index = first_curly
            close_bracket = '}'
        else:
            start_index = first_square
            close_bracket = ']'

    # Find the last occurrence of that bracket
    end_index = text.rfind(close_bracket)
    if end_index == -1 or end_index < start_index:
        return original_text

    # Extract the substring
    json_substring = text[start_index:end_index + 1]

    # Remove only actual JS-style comments outside strings
    json_substring = remove_js_style_comments_outside_strings(json_substring)

    # Attempt to parse the cleaned substring
    try:
        parsed = json.loads(json_substring)
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        # If it fails, just return the original
        return original_text


def parse_workflow_json(result: str) -> str:
    # Function to replace single quotes with double quotes and handle True/False
    def convert_to_json_compliant_string(text: str) -> str:
        # Convert Python-style booleans to JSON booleans (True -> true, False -> false)
        text = text.replace("True", "true").replace("False", "false")

        # Replace single quotes with double quotes for strings
        # This replacement will happen only for string-like values (inside curly braces or key-value pairs)
        text = re.sub(r"(?<=:)\s*'(.*?)'\s*(?=\s*,|\s*\})", r'"\1"', text)  # For values
        text = re.sub(r"(?<=,|\{|\[)\s*'(.*?)'\s*(?=\s*:|\s*,|\s*\])", r'"\1"', text)  # For keys

        # Ensure the surrounding quotes around strings
        text = re.sub(r"(?<=:)\s*'(.*?)'\s*(?=\s*,|\s*\})", r'"\1"', text)
        return text

    # If result is a dictionary, convert it to JSON with double quotes
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)

    # If result is a string, process it for improper quote handling
    if isinstance(result, str):
        if result.startswith("```json"):
            # Extract the content inside the json code block
            start_index = result.find("```json") + len("```json\n")
            end_index = result.find("```", start_index)
            json_content = result[start_index:end_index].strip()

            # Apply the corrections: Convert single quotes, True/False to JSON-compatible format
            json_content = convert_to_json_compliant_string(json_content)

            # Try to parse the extracted content as JSON
            try:
                parsed_json = json.loads(json_content)
                return json.dumps(parsed_json, ensure_ascii=False)
            except json.JSONDecodeError:
                return json_content  # If parsing fails, return the original content as is
        elif result.startswith("```"):
            # If result is a general code block, strip the backticks and return it
            return "\n".join(result.split("\n")[1:-1])
        else:
            # Apply the corrections to the string content
            result = convert_to_json_compliant_string(result)
            return result

    # Return result as-is if it's neither a dictionary nor a valid string format
    return result


def main():
    # Example input
    input_data = """
Here is an example JSON data structure for the entity `data_analysis_job`, reflecting the business logic based on the user's requirement to analyze London Houses data using pandas:

```json
{
  "job_id": "data_analysis_job_001",
  "job_name": "Analyze London Houses Data",
  "job_status": "completed",
  "start_time": "2023-10-01T10:05:00Z",
  "end_time": "2023-10-01T10:30:00Z",
  "input_data": {
    "raw_data_entity_id": "raw_data_entity_001",
    "data_source": "https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/london_houses.csv"
  },
  "analysis_parameters": {
    "metrics": [
      {
        "name": "average_price",
        "description": "Calculate the average price of the houses.",
        "value": 1371200
      },
      {
        "name": "median_square_meters",
        "description": "Find the median square meters of the houses.",
        "value": 168
      }
    ],
    "filters": {
      "neighborhood": ["Notting Hill", "Westminster"],
      "min_bedrooms": 2,
      "max_bathrooms": 3
    }
  },
  "analysis_results": {
    "total_houses_analyzed": 3,
    "houses_with_garden": 2,
    "houses_with_parking": 1,
    "price_distribution": {
      "min_price": 1476000,
      "max_price": 2291200,
      "average_price": 1371200
    },
    "visualizations": [
      {
        "type": "bar_chart",
        "title": "Price Distribution by Neighborhood",
        "data": [
          {
            "neighborhood": "Notting Hill",
            "count": 1,
            "average_price": 2291200
          },
          {
            "neighborhood": "Westminster",
            "count": 1,
            "average_price": 1476000
          },
          {
            "neighborhood": "Soho",
            "count": 1,
            "average_price": 1881600
          }
        ]
      },
      {
        "type": "scatter_plot",
        "title": "Square Meters vs Price",
        "data": [
          {
            "square_meters": 179,
            "price": 2291200
          },
          {
            "square_meters": 123,
            "price": 1476000
          },
          {
            "square_meters": 168,
            "price": 1881600
          }
        ]
      }
    ]
  },
  "report_output": {
    "report_id": "report_001",
    "report_format": "PDF",
    "generated_at": "2023-10-01T10:35:00Z",
    "report_link": "https://example.com/reports/report_001.pdf"
  }
}
```

### Explanation
- **job_id, job_name, job_status**: Basic identifiers and status of the analysis job.
- **input_data**: Contains references to the raw data entity that is being analyzed and where the data is sourced from.
- **analysis_parameters**: Specifies the metrics to be calculated and any filters applied during the analysis.
- **analysis_results**: Summarizes the outcomes of the data analysis, including total houses analyzed, distribution of prices, and visual representations of the results.
- **report_output**: Information about the generated report, including its format, generation time, and a link to access it. 

This JSON structure provides a comprehensive overview of the analysis conducted on the London Houses data, reflecting the required business logic for the `data_analysis_job` entity.   """
    output_data = parse_json(input_data)

    print(output_data)


if __name__ == "__main__":
    main()


async def validate_result(data: str, file_path: str, schema: Optional[str]) -> str:
    if file_path:
        try:
            async with aiofiles.open(file_path, "r") as schema_file:
                content = await schema_file.read()
                schema = json.load(content)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading schema file {file_path}: {e}")
            raise

    try:
        parsed_data = parse_json(data)
        json_data = json.loads(parsed_data)
        normalized_json_data = _normalize_boolean_json(json_data)
        validate(instance=normalized_json_data, schema=schema)
        logger.info("JSON validation successful.")
        return normalized_json_data
    except jsonschema.exceptions.ValidationError as err:
        logger.error(f"JSON schema validation failed: {err.message}")
        raise ValidationErrorException(message=f"JSON schema validation failed: {err}, {err.message}")
    except json.JSONDecodeError as err:
        logger.error(f"Failed to decode JSON: {err}")
        try:
            parsed_data = parse_json(data)
            errors = consolidate_json_errors(parsed_data)
        except Exception as e:
            logger.error(f"Failed to consolidate JSON errors: {e}")
            errors = [str(e)]
        raise ValidationErrorException(
            message=f"Failed to decode JSON: {err}, {err.msg}, {errors} . Please make sure the json returned is correct and aligns with json formatting rules. make sure you're using quotes for string values, including None")
    except Exception as err:
        logger.error(f"Unexpected error during JSON validation: {err}")
        raise ValidationErrorException(message=f"Unexpected error during JSON validation: {err}")


def consolidate_json_errors(json_str):
    errors = []

    # Try to parse the JSON string
    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        errors.append(f"JSONDecodeError: {e}")

        # Extract the problematic part of the JSON string
        error_pos = e.pos
        error_line = json_str.count('\n', 0, error_pos) + 1
        error_col = error_pos - json_str.rfind('\n', 0, error_pos)

        errors.append(f"Error at line {error_line}, column {error_col}")

        # Try to find the context around the error
        context_start = max(0, error_pos - 20)
        context_end = min(len(json_str), error_pos + 20)
        context = json_str[context_start:context_end]
        errors.append(f"Context around error: {context}")

        # Attempt to fix common JSON issues
        # Example: Fixing unescaped quotes
        fixed_json_str = re.sub(r'(?<!\\)"', r'\"', json_str)

        try:
            json_data = json.loads(fixed_json_str)
            errors.append("JSON was successfully parsed after fixing unescaped quotes.")
        except json.JSONDecodeError as e:
            errors.append("Failed to fix JSON after attempting to fix unescaped quotes.")

    return errors


async def read_file(file_path: str):
    """Read and return JSON entity from a file."""
    try:
        async with aiofiles.open(file_path, 'r') as file:
            content = await file.read()
            return content
    except Exception as e:
        logger.error(f"Failed to read JSON file {file_path}: {e}")
        raise  # Re-raise the exception for further handling


async def read_file_object(file_path: str):
    """Asynchronously read and return a file object for the given file path with a file size limit check."""
    try:
        # First, check the file size before opening it
        # todo blocking!!!
        file_size = os.path.getsize(file_path)

        if file_size > config.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds the {config.MAX_FILE_SIZE} byte limit")

        # Now open the file asynchronously if the size is within limits
        async with aiofiles.open(file_path, 'rb') as file:
            return file
    except Exception as e:
        logger.error(f"Failed to open file {file_path}: {e}")
        raise


async def read_json_file(file_path: str):
    try:
        async with aiofiles.open(file_path, "r") as file:
            content = await file.read()  # Read the file content asynchronously
            data = json.loads(content)  # Parse the content as JSON
        logger.info(f"Successfully read JSON file: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed for file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading the file {file_path}: {e}")
        raise


def _invalidate_tokens(cyoda_auth_service: CyodaAuthService):
    """Delegate token invalidation to the provided token service."""
    cyoda_auth_service.invalidate_tokens()


async def send_cyoda_request(
        cyoda_auth_service: CyodaAuthService,
        method: str,
        path: str,
        data: Any = None,
        base_url: str = config.CYODA_API_URL
) -> dict:
    """
    Send an HTTP request to the Cyoda API with automatic retry on 401.
    """
    token = cyoda_auth_service.get_access_token()
    max_attempt = 5
    for attempt in range(max_attempt):
        try:
            if method.lower() == "get":
                resp = await send_get_request(token, base_url, path)
            elif method.lower() == "post":
                resp = await send_post_request(token, base_url, path, data=data)
            elif method.lower() == "put":
                resp = await send_put_request(token, base_url, path, data=data)
            elif method.lower() == "delete":
                resp = await send_delete_request(token, base_url, path)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            # todo check here
        except Exception as exc:
            if exc and hasattr(exc, "status_code"):
                if attempt == 0 and exc.status_code==401:
                    logger.warning(f"Request to {path} failed with 401; invalidating tokens and retrying")
                    _invalidate_tokens(cyoda_auth_service=cyoda_auth_service)
                    token = cyoda_auth_service.get_access_token()
                    continue
                elif attempt <= max_attempt and exc.status_code==422:
                    logger.error(f"Response from {path} returned status 422; retrying")
                    continue
                elif attempt <= max_attempt and exc.status_code in [500, 503]:
                    logger.error(f"Response from {path} returned status 500; retrying")
                    continue
            else:
                msg = str(exc)
                if attempt == 0 and ("401" in msg or "Unauthorized" in msg):
                    logger.warning(f"Request to {path} failed with 401; invalidating tokens and retrying")
                    _invalidate_tokens(cyoda_auth_service=cyoda_auth_service)
                    token = cyoda_auth_service.get_access_token()
                    continue
                elif attempt <= max_attempt and ("422" in msg):
                    logger.error(f"Response from {path} returned status 422; retrying")
                    continue
                elif attempt <= max_attempt and (("500" in msg) or ("503" in msg)):
                    logger.error(f"Response from {path} returned status 500; retrying")
                    continue
            raise
        status = resp.get("status") if isinstance(resp, dict) else None
        if attempt == 0 and status == 401:
            logger.warning(f"Response from {path} returned status 401; invalidating tokens and retrying")
            _invalidate_tokens(cyoda_auth_service=cyoda_auth_service)
            token = cyoda_auth_service.get_access_token()
            continue
        return resp
    raise RuntimeError(f"Failed request {method.upper()} {path} after retry")


async def send_get_request(token: str, api_url: str, path: str) -> Optional[Any]:
    url = f"{api_url}/{path}" if path else api_url
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = await send_request(headers, url, 'GET', None, None)
        # Raise an error for bad status codes
        logger.debug(f"GET request to {url} successful.")
        return response
    except Exception as err:
        logger.error(f"Error during GET request to {url}: {err}")
        raise

async def send_request(
        headers: dict,
        url: str,
        method: str,
        data: Optional[dict] = None,
        json_data: Optional[dict] = None,
) -> dict:
    """
    Send an HTTP request with the given headers and payload.

    - All 2xx are treated as success.
    - GET/POST also allow 404 (returned as content).
    - PUT/DELETE will raise on 404.
    - Raises InvalidTokenException on 401.
    - Logs & raises on any other non-allowed status.
    """
    method = method.upper()
    if method not in {"GET", "POST", "PUT", "DELETE"}:
        raise ValueError(f"Unsupported HTTP method: {method!r}")

    # Which statuses we’ll accept without exception:
    allowed_statuses: Set[int] = set(range(200, 300))
    if method in ("GET", "POST"):
        allowed_statuses.add(404)

    timeout = httpx.Timeout(150.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
        response = await client.request(
            method, url, headers=headers, data=data, json=json_data
        )

    status = response.status_code

    if status == 401:
        raise InvalidTokenException("The service returned Invalid token")

    if status not in allowed_statuses:
        # unexpected status → log full context then raise
        logger.error(
            f"url={url}, method={method}, data={json.dumps(data or json_data)}"
        )
        response.raise_for_status()

    if status == 404 and method == "POST":
        logger.warning(
            f"status={status}. url={url}, method={method}, data={json.dumps(data or json_data)}"
        )

    # parse body (JSON if we can, otherwise raw text)
    content: Optional[any]
    ct = response.headers.get("Content-Type", "")
    if "application/json" in ct:
        try:
            content = response.json()
        except ValueError:
            logger.warning(f"Failed to parse JSON for {method} {url}; falling back to text")
            content = response.text
    else:
        content = response.text

    return {"status": status, "json": content}



async def send_post_request(token: str, api_url: str, path: str, data=None, json=None) -> Optional[Any]:
    url = f"{api_url}/{path}" if path else api_url
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = await send_request(headers, url, 'POST', data, json)
        return response
    except Exception as err:
        logger.error(f"Error during POST request to {url}: {err}")
        raise


async def send_put_request(token: str, api_url: str, path: str, data=None, json=None) -> Optional[Any]:
    url = f"{api_url}/{path}" if path else api_url
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = await send_request(headers, url, 'PUT', data, json)
        logger.info(f"PUT request to {url} successful.")
        return response
    except Exception as err:
        logger.error(f"Error during PUT request to {url}: {err}")
        raise


async def send_delete_request(token: str, api_url: str, path: str) -> Optional[Any]:
    url = f"{api_url}/{path}" if path else api_url
    token = f"Bearer {token}" if not token.startswith('Bearer') else token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{token}",
    }
    try:
        response = await send_request(headers, url, 'DELETE', None, None)
        logger.info(f"GET request to {url} successful.")
        return response
    except Exception as err:
        logger.error(f"Error during GET request to {url}: {err}")
        raise


def expiration_date(seconds: int) -> int:
    return int((time.time() + seconds) * 1000.0)


def now():
    timestamp = int(time.time() * 1000.0)
    return timestamp


def timestamp_before(seconds: int) -> int:
    return int((time.time() - seconds) * 1000.0)


def clean_formatting(text):
    """
    Convert multi-line text into a single line, preserving all other content.
    """
    # Replace any sequence of newlines (and carriage returns) with a single space
    return re.sub(r'[\r\n]+', ' ', text)


# def clean_formatting(text):
#     """
#     This function simulates the behavior of text pasted into Google search:
#     - Removes leading and trailing whitespace.
#     - Condenses multiple spaces into a single space.
#     - Keeps alphanumeric characters and spaces only, removing other characters.
#
#     :param answer: The input string to be cleaned
#     :return: A cleaned string
#     """
#     # Remove leading and trailing whitespace
#     text = text.strip()
#
#     # Condense multiple spaces into a single space
#     text = re.sub(r'\s+', ' ', text)
#
#     # Remove non-alphanumeric characters (excluding spaces)
#     text = re.sub(r'[^\w\s]', '', text)
#
#     return text

def current_timestamp():
    now = datetime.now(ZoneInfo("UTC"))
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]


def custom_serializer(obj):
    if isinstance(obj, queue.Queue):
        # Convert queue to list
        return list(obj.queue)
    if not isinstance(obj, dict):
        # Convert the object to a dictionary. Customize as needed.
        return obj.__dict__
    raise TypeError(f"Type {type(obj)} not serializable")


def format_json_if_needed(data, key):
    value = data.get(key)
    if isinstance(value, dict):
        # Pretty print the JSON object
        formatted_json = json.dumps(value, indent=4)
        data[key] = f"```json \n{formatted_json}\n```"
    else:
        print(f"Data at {key} is not a valid JSON object: {value}")  # Optionally log this or handle it
    return data

async def clone_repo(git_branch_id: str, repository_name: str):
    """
    Clone the GitHub repository to the target directory.
    If the repository should not be copied, it ensures the target directory exists.
    """
    repository_url = config.REPOSITORY_URL.format(repository_name=repository_name)
    clone_dir = f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}"

    if await repo_exists(clone_dir):
        await git_pull(git_branch_id=git_branch_id, repository_name=repository_name)
        return

    if config.CLONE_REPO != "true":
        # Create the directory asynchronously using asyncio.to_thread
        await asyncio.to_thread(os.makedirs, clone_dir, exist_ok=True)
        logger.info(f"Target directory '{clone_dir}' is created.")
        return

    # Asynchronously clone the repository using subprocess

    clone_process = await asyncio.create_subprocess_exec(
        'git', 'clone', repository_url, clone_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await clone_process.communicate()

    if clone_process.returncode != 0:
        logger.error(f"Error during git clone: {stderr.decode()}")
        return

    # Asynchronously checkout the branch using subprocess
    checkout_process = await asyncio.create_subprocess_exec(
        'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
        'checkout', '-b', str(git_branch_id),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await checkout_process.communicate()

    if checkout_process.returncode != 0:
        logger.error(f"Error during git checkout: {stderr.decode()}")
        return

    logger.info(f"Repository cloned to {clone_dir}")

    os.chdir(clone_dir)
    await set_upstream_tracking(git_branch_id=git_branch_id)
    await run_git_config_command()
    await git_pull(git_branch_id=git_branch_id, repository_name=repository_name)


async def get_project_file_name(git_branch_id, file_name, repository_name: str, folder_name=None):
    if folder_name:
        project_file_name = f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}/{folder_name}/{file_name}"
    else:
        project_file_name = f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}/{file_name}"
    await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)
    return project_file_name


async def get_project_file_name_path(technical_id, git_branch_id, file_name, repository_name: str):
    await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)
    target_dir = os.path.join(f"{config.PROJECT_DIR}/{technical_id}/{repository_name}", "")
    file_path = os.path.join(target_dir, file_name)
    return file_path

async def _save_file(_data, item, git_branch_id, repository_name: str, folder_name = None) -> str:
    """
    Save a file (text or binary) inside a specific directory.
    Handles FileStorage objects directly.
    """
    await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)
    target_dir = os.path.join(f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}", folder_name or "")
    file_path = os.path.join(target_dir, item)
    logger.info(f"Saving to {file_path}")

    # Use asyncio.to_thread for non-blocking creation of directories
    await asyncio.to_thread(os.makedirs, os.path.dirname(file_path), exist_ok=True)

    # Process the _data and get the output to save
    try:
        # Handle FileStorage object directly
        if hasattr(_data, "read"):  # Check if `_data` is a file-like object
            _data.seek(0)  # Ensure we're at the beginning of the file
            write_mode = 'wb'  # Assume binary mode for file-like objects
            async with aiofiles.open(file_path, write_mode) as output:
                file_data = _data.read()  # Read the data directly, no need to await
                await output.write(file_data)  # Now you can await the write operation
        else:
            # Process and save as text or binary

            if isinstance(_data, dict):
                output_data = json.dumps(_data)
            elif isinstance(_data, list):
                output_data = json.dumps(_data)
            else:
                output_data = _data
            write_mode = 'w' if isinstance(output_data, str) else 'wb'
            async with aiofiles.open(file_path, write_mode) as output:

                await output.write(output_data)
    except Exception as e:
        logger.error(f"Failed to save file {file_path}: {e}")
        raise

    logger.info(f"Saved to {file_path}")
    file_paths_to_commit = [file_path]

    if repository_name == config.PYTHON_REPOSITORY_NAME:
        # Define the path for __init__.py in the target directory
        init_file_target_dir = os.path.dirname(file_path)
        init_file = os.path.join(init_file_target_dir, "__init__.py")


        # Check if __init__.py exists asynchronously
        init_file_exists = await asyncio.to_thread(os.path.exists, init_file)

        if not init_file_exists:
            # If __init__.py does not exist, create it (empty __init__.py file)
            async with aiofiles.open(init_file, 'w') as f:
                pass  # Just create an empty __init__.py file

            logger.info(f"Created {init_file}")
            file_paths_to_commit.append(init_file)

    if config.CLONE_REPO == "true":
        await _git_push(git_branch_id=git_branch_id,
                        file_paths=file_paths_to_commit,
                        commit_message=f"saved {item}",
                        repository_name=repository_name)

    logger.info(f"pushed to git")

    return str(file_path)


async def delete_file(_data, item, git_branch_id, repository_name: str, folder_name=None) -> str:
    """
    Delete a file inside a specific directory in a cloned repository.
    If config.CLONE_REPO is true, pushes the deletion to the repository.
    """
    await clone_repo(git_branch_id=git_branch_id, repository_name=repository_name)
    target_dir = os.path.join(f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}", folder_name or "")
    file_path = os.path.join(target_dir, item)

    logger.info(f"Attempting to delete: {file_path}")

    # Ensure target directory exists before attempting to delete
    await asyncio.to_thread(os.makedirs, os.path.dirname(file_path), exist_ok=True)

    # Delete file
    if os.path.isfile(file_path):
        await asyncio.to_thread(os.remove, file_path)
        logger.info(f"Deleted file: {file_path}")
    else:
        logger.warning(f"File not found for deletion: {file_path}")

    # Push changes to Git if cloning is enabled
    if config.CLONE_REPO == "true":
        await _git_push(git_branch_id=git_branch_id,
                        file_paths=[item],
                        commit_message=f"deleted {item}",
                        repository_name=repository_name)
        logger.info("Pushed deletion to git")

    return str(file_path)


async def git_pull(git_branch_id, repository_name: str, merge_strategy="recursive"):
    clone_dir = f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}"

    try:
        # Start the `git checkout` command asynchronously
        checkout_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'checkout', str(git_branch_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await checkout_process.communicate()

        if checkout_process.returncode != 0:
            logger.error(f"Error during git checkout: {stderr.decode()}")
            return

        # Fetch latest changes from remote (without merging them yet)
        fetch_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'fetch', 'origin',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        fetch_stdout, fetch_stderr = await fetch_process.communicate()

        if fetch_process.returncode != 0:
            logger.error(f"Error during git fetch: {fetch_stderr.decode()}")
            return

        # Compare the local branch with its remote counterpart explicitly
        diff_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'diff', f"origin/{str(git_branch_id)}", str(git_branch_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        diff_stdout, diff_stderr = await diff_process.communicate()

        if diff_process.returncode != 0:
            logger.error(f"Error during git diff: {diff_stderr.decode()}")
            return

        # Capture the full diff result before pull
        diff_result_before_pull = diff_stdout.decode()
        logger.info(f"Git diff (before pull): {diff_result_before_pull}")

        # If no diff, skip the pull
        if not diff_result_before_pull.strip():
            logger.info("No changes to pull, skipping pull.")
            return diff_result_before_pull  # Just return the diff with no changes

        # Now, run the `git pull` command asynchronously with the specified merge strategy
        pull_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'pull', '--strategy', merge_strategy, '--strategy-option=theirs', 'origin', str(git_branch_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        pull_stdout, pull_stderr = await pull_process.communicate()

        if pull_process.returncode != 0:
            logger.error(f"Error during git pull: {pull_stderr.decode()}")
            return

        logger.info(f"Git pull successful: {pull_stdout.decode()}")

        # Return the full diff before pull as the result
        return diff_result_before_pull

    except Exception as e:
        logger.error(f"Unexpected error during git pull: {e}")
        logger.exception(e)


# todo git push in case of interim changes will throw an error
async def _git_push(git_branch_id, file_paths: list, commit_message: str, repository_name: str):
    await git_pull(git_branch_id=git_branch_id, repository_name=repository_name)

    clone_dir = f"{config.PROJECT_DIR}/{git_branch_id}/{repository_name}"

    try:
        # Create a new branch with the name git_branch_id
        checkout_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'checkout', str(git_branch_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await checkout_process.communicate()
        if checkout_process.returncode != 0:
            logger.error(f"Error during git checkout: {stderr.decode()}")
            return

        # Add files to the commit
        for file_path in file_paths:
            add_process = await asyncio.create_subprocess_exec(
                'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
                'add', file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await add_process.communicate()
            if add_process.returncode != 0:
                logger.error(f"Error during git add {file_path}: {stderr.decode()}")
                return

        # Commit the changes
        commit_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'commit', '-m', f"{commit_message}: {git_branch_id}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await commit_process.communicate()
        if commit_process.returncode != 0:
            logger.error(f"Error during git commit: {stderr.decode()}")
            return

        # Push the new branch to the remote repository
        push_process = await asyncio.create_subprocess_exec(
            'git', '--git-dir', f"{clone_dir}/.git", '--work-tree', clone_dir,
            'push', '-u', 'origin', str(git_branch_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await push_process.communicate()
        if push_process.returncode != 0:
            logger.error(f"Error during git push: {stderr.decode()}")
            return

        logger.info("Git push successful!")

    except Exception as e:
        logger.error(f"Unexpected error during git push: {e}")
        logger.exception(e)


async def repo_exists(path: str) -> bool:
    # Run the blocking os.path.exists in a separate thread
    return await asyncio.to_thread(os.path.exists, path)


async def run_git_config_command():
    process = await asyncio.create_subprocess_exec(
        "git", "config", "pull.rebase", "false", "--global",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed with error: {stderr.decode().strip()}")
    print(stdout.decode().strip())


async def set_upstream_tracking(git_branch_id):
    branch = git_branch_id
    # Construct the command to set the upstream branch
    process = await asyncio.create_subprocess_exec(
        "git", "branch", "--set-upstream-to", f"origin/{branch}", branch,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"Error setting upstream: {stderr.decode().strip()}")
    else:
        print(f"Successfully set upstream tracking for branch {branch}.")

def validate_token(token):
    try:
        payload = jwt.decode(token, config.AUTH_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()


def parse_from_string(escaped_code: str) -> str:
    """
    Convert a string containing escape sequences into its normal representation.

    Args:
        escaped_code: A string with literal escape characters (e.g. "\\n").

    Returns:
        A string with actual newlines and other escape sequences interpreted.
    """
    # Using the 'unicode_escape' decoding to process the escape sequences
    return escaped_code.encode("utf-8").decode("unicode_escape")


def parse_entity(model_cls, resp: Any) -> Any:
    try:
        if model_cls:
            if isinstance(resp, list):

                return [model_cls.model_validate(item) for item in resp]

            else:
                if not isinstance(resp, model_cls):
                    return model_cls.model_validate(resp)
                return resp
        return resp
    except Exception as e:
        logger.exception(e)
        return None


async def read_file_util(filename, technical_id, repository_name: str):
    await git_pull(git_branch_id=technical_id, repository_name=repository_name)
    target_dir = os.path.join(f"{config.PROJECT_DIR}/{technical_id}/{repository_name}", "")
    file_path = os.path.join(target_dir, filename)
    try:
        async with aiofiles.open(file_path, 'r') as file:
            content = await file.read()
        return content
    except FileNotFoundError:
        return ''
    except Exception as e:
        logger.exception("Error during reading file")
        return f"Error during reading file: {e}"


def wrap_response_by_extension(filename: str, response: str) -> str:
    """
    Wrap the given response string in a Markdown code fence based on the file extension of filename.

    Args:
        filename: The name (or path) of the output file.
        response: The content to wrap in a code block.

    Returns:
        A Markdown-formatted string with the response wrapped in a code fence and appropriate language hint.
    """
    # Extract the file extension (without the leading dot) and normalize
    _, ext = os.path.splitext(filename)
    ext = ext.lower().lstrip('.')

    # Mapping from extensions to Markdown language identifiers
    lang_map = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'java': 'java',
        'html': 'html',
        'css': 'css',
        'json': 'json',
        'xml': 'xml',
        'sh': 'bash',
        'rb': 'ruby',
        'go': 'go',
        'php': 'php',
        # Add more mappings as needed
    }

    # Determine the language for the code fence
    language = lang_map.get(ext)

    # Wrap in Markdown code fence
    if language:
        return f"```{language}\n{response}\n```"
    else:
        # Fallback to a generic code block if unknown extension
        return f"```\n{response}\n```"


def _post_process_response(response: str, config: dict) -> str:
    """
    Post-process the response by formatting and wrapping based on output configuration.

    - If a local filesystem output is specified, inspects the first filename.
    - For JSON files, parses and pretty-prints JSON before wrapping.
    - Wraps all responses in a code fence matching the file extension.

    Args:
        response: Raw response content.
        config: Configuration dict, expecting {'output': {'local_fs': [filenames]}}.

    Returns:
        The formatted and/or wrapped response, or the original response if no output is configured.
    """
    # Safely retrieve local_fs list
    local_files = config.get('output', {}).get('local_fs') or []
    if not local_files:
        return response

    filename = local_files[0]
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    # Handle JSON formatting
    if ext == '.json':
        try:
            parsed = json.loads(response)
            response = json.dumps(parsed, indent=4, sort_keys=True)
        except json.JSONDecodeError as err:
            logger.error("Invalid JSON format for file %s: %s", filename, err)
            # Fall back to raw response on error

    # Wrap based on extension
    return wrap_response_by_extension(filename, response)

def get_current_timestamp_num(lower_timedelta=0):
    time_now = datetime.now(timezone.utc)
    if lower_timedelta > 0:
        time_ago = time_now - timedelta(seconds=lower_timedelta)
        epoch_millis = int(time_ago.timestamp() * 1000)
        return epoch_millis
    else:
        epoch_millis = int(time_now.timestamp() * 1000)
        return epoch_millis

def get_repository_name(entity: "WorkflowEntity"):
    programming_language = entity.workflow_cache.get("programming_language")
    if programming_language:
        if programming_language == "PYTHON":
            return config.PYTHON_REPOSITORY_NAME
        if programming_language == "JAVA":
            return config.JAVA_REPOSITORY_NAME
    repository_name = config.JAVA_REPOSITORY_NAME if entity.workflow_name.endswith(
        "java") else config.PYTHON_REPOSITORY_NAME
    return repository_name