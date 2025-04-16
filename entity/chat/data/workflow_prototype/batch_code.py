# Upload the file (adjust the 'purpose' as needed for your batch process)
import asyncio
import io

import aiofiles
from openai import AsyncOpenAI

client=AsyncOpenAI()

output_filename = "state_diagram_batch.jsonl"

# Asynchronous function to upload a file.
async def upload_file_async(output_filename):
    # Read the file asynchronously.
    async with aiofiles.open(output_filename, "rb") as f:
        file_data = await f.read()
    # Wrap the file data in a BytesIO object (if required by the API).
    file_obj = io.BytesIO(file_data)
    batch_input_file = await client.files.create(
        file=file_obj,
        purpose="batch"  # Use the appropriate purpose.
    )
    print("Uploaded file with ID:", batch_input_file.id)
    return batch_input_file

# Asynchronous function to create a batch job.
async def create_batch_job_async(batch_input_file):
    batch_job = await client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "nightly eval job"
        }
    )
    print("Created batch job:", batch_job)
    return batch_job

# Asynchronous function to poll until the batch job is complete.
async def wait_until_completed_async(batch_job):
    while True:
        retrieved_batch = await client.batches.retrieve(batch_job.id)
        # Adjust the check below based on the actual attribute your API uses.
        if getattr(retrieved_batch, "status", None) == "completed":
            break
        print("Batch job not completed yet, waiting...")
        await asyncio.sleep(10)  # wait 10 seconds before checking again
    print("Batch job completed:", retrieved_batch)
    return retrieved_batch

# Asynchronous function to retrieve and print the file content.
async def retrieve_file_content_async(retrieved_batch):
    file_response = await client.files.content(retrieved_batch.output_file_id)
    print("File content:")
    print(file_response.text)
    return file_response.text

# Main asynchronous function that ties everything together.
async def main():
    batch_input_file = await upload_file_async(output_filename)
    batch_job = await create_batch_job_async(batch_input_file)
    retrieved_batch = await wait_until_completed_async(batch_job)
    await retrieve_file_content_async(retrieved_batch)

if __name__ == '__main__':
    asyncio.run(main())