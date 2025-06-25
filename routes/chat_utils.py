from quart import request

from common.utils.auth_utils import get_user_id


async def extract_auth_info():
    header = request.headers.get('Authorization', '')
    user_id = await get_user_id(header) if header else None
    return header, user_id


async def get_json_data(*keys):
    data = await request.get_json()
    return (data.get(k) for k in keys)


async def get_form_data(*keys, file_key=None):
    form = (await request.form).to_dict()
    files = await request.files
    return tuple(form.get(k) for k in keys), files.get(file_key) if file_key else None
