import asyncio
import json

try:
    from openai import AsyncOpenAI
    client = AsyncOpenAI()
except Exception:
    # Mock client for testing or when OpenAI is not available
    class MockAsyncOpenAI:
        def __init__(self):
            pass
    client = MockAsyncOpenAI()

async def process_item(item: dict):
    """
    Processes a single JSON object from the file.
    It sends an async request to OpenAI if method is POST.
    Returns a tuple (custom_id, response).
    """
    custom_id = item.get("custom_id")
    if item.get("method", "POST").upper() != "POST":
        return custom_id, {"error": f"Unsupported method: {item.get('method')}"}

    body = item.get("body", {})

    try:
        # Call the async chat completion API using the provided body.
        response = await client.chat.completions.create(**body)
        content = response.choices[0].message.content
        if content is None:
            content = {"error": "Response structure missing message content"}
    except Exception as e:
        content = {"error": str(e)}

    return custom_id, content


async def batch_process_file(input_file_path: str, output_file_path: str):
    """
    Reads the JSONL file, creates tasks for each line, and gathers the responses concurrently.
    The final responses are sorted by custom_id.
    """
    tasks = []
    with open(input_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                tasks.append(process_item(item))

    responses = await asyncio.gather(*tasks)

    # Sort responses by custom_id (assuming they are numeric strings; adjust if needed)
    responses_sorted = sorted(
        responses,
        key=lambda x: int(x[0]) if str(x[0]).isdigit() else x[0]
    )
    # Write the result JSON to a file.
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(responses_sorted, f, indent=2)
    return output_file_path


async def build_workflow_from_jsonl(input_file_path):
    with open(input_file_path, "r", encoding="utf-8") as f:
        responses = json.loads(f.read())
    states = {}
    for custom_id, response in responses:
        # Parse the response into a dictionary
        try:
            state_update = json.loads(response) if isinstance(response, str) else response
        except Exception as e:
            # Log or handle parsing errors as needed
            state_update = {"error": f"Parsing error: {str(e)}"}

        # Process each state in the update
        for state_id, new_state in state_update.items():
            # If the state already exists, merge the transitions
            if state_id in states:
                existing_state = states[state_id]
                new_transitions = new_state.get("transitions")
                if new_transitions and isinstance(new_transitions, dict):
                    # Ensure the existing state's transitions is a dictionary
                    if "transitions" not in existing_state or not isinstance(existing_state["transitions"], dict):
                        existing_state["transitions"] = {}
                    existing_state["transitions"].update(new_transitions)
                else:
                    # Optionally merge the rest of the keys if no transitions are provided
                    existing_state.update(new_state)
            else:
                # If the state doesn't exist, add it directly
                states[state_id] = new_state
    return {"initial_state": "none", "states": states}

def main():

    input_file_path = "state_diagram_batch_40ebbd13-37e9-4844-829e-5a7a56bb40a7.jsonl"
    output_file_path = f"processed_workflow_{input_file_path.split('.')[0]}.json"
    result = asyncio.run(batch_process_file(input_file_path=input_file_path, output_file_path=output_file_path))
    result = asyncio.run(build_workflow_from_jsonl(output_file_path))
    output_file = f"generated_workflow_{input_file_path.split('.')[0]}.json"
    # Write the result JSON to a file.
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == '__main__':
    main()