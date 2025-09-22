from quart import request

from common.utils.auth_utils import get_user_id


async def extract_auth_info():
    header = request.headers.get('Authorization', '')
    user_id = await get_user_id(header) if header else None
    return header, user_id


async def get_json_data(*keys):
    data = await request.get_json()
    return (data.get(k) for k in keys)


async def get_form_data(*keys, file_key=None, files_key=None):
    form = (await request.form).to_dict()
    files = await request.files

    # Handle single file (backward compatibility)
    single_file = files.get(file_key) if file_key else None

    # Handle multiple files (new functionality)
    multiple_files = None
    if files_key:
        # Get all files with the specified key (supports multiple files with same name)
        multiple_files = files.getlist(files_key)
        if not multiple_files:
            multiple_files = None

    return tuple(form.get(k) for k in keys), single_file, multiple_files


async def get_mixed_data(*keys, file_key=None, files_key=None):
    """
    Handle mixed JSON and file data for endpoints that need both.
    First tries to get JSON data, then falls back to form data with files.
    """
    content_type = request.headers.get('Content-Type', '')

    if content_type.startswith('application/json'):
        # JSON only request (no files)
        data = await request.get_json()
        return tuple(data.get(k) for k in keys), None, None
    else:
        # Form data request (potentially with files)
        return await get_form_data(*keys, file_key=file_key, files_key=files_key)
