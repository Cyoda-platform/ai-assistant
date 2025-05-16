import logging
import re
import json
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(threadName)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

def extract_and_validate_json(text: str) -> str:
    # Search for a Python code block in the provided text.
    # The code block should be enclosed within triple backticks and start with "python".
    if isinstance(text, dict):
        return text
    try:
        match = re.search(r'```json(.*?)```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()

        # Attempt to parse the extracted code using libcst.
        valid_json = json.loads(text)
    except Exception as e:
        # If parsing fails, return an error message.
        logger.exception(e)
        raise e

    # If parsing is successful, return the valid Python code.
    return valid_json

if __name__ == "__main__":
    input = r'''
```json{"hello": "hello"}```
        '''
    json = extract_and_validate_json(input)
    print(json)