import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union
from zoneinfo import ZoneInfo

from common.workflow.workflow_to_dto_converter import VALID_VALUE_TYPES, FIELD_NAME_PREFIX, VALUE_TYPE_TO_JAVA_TYPE, \
    RAW_TYPES, META_FIELD_TYPES


def generate_id() -> str:
    """Generates a time-based UUID string."""
    return str(uuid.uuid1())


def current_timestamp() -> str:
    """Returns current UTC timestamp in ISO 8601 format with timezone offset."""
    now = datetime.now(ZoneInfo("UTC"))
    return now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]


def read_json_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Reads and parses a JSON file."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(path: Union[str, Path], data: Dict[str, Any]) -> None:
    """Serializes and writes a JSON-compatible dict to a file."""
    path = Path(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def resolve_field_name(json_path: str, value_type: str) -> str:
    """
    Resolves a JSON path to a Cyoda-compatible field name, using known prefixes.
    Raises ValueError if value_type is invalid.
    """
    if value_type not in VALID_VALUE_TYPES:
        raise ValueError(
            f"Invalid value_type '{value_type}'. Must be one of: {', '.join(sorted(VALID_VALUE_TYPES))}"
        )
    return f"{FIELD_NAME_PREFIX}{value_type}.[{json_path}]"


def map_value_type_to_java_type(value_type: str) -> Union[str, None]:
    """Maps abstract value_type to concrete Java type string."""
    return VALUE_TYPE_TO_JAVA_TYPE.get(value_type)


def build_between_value(field_name: str, value: Any, value_type: str) -> Any:
    """
    Wraps a value in @type declaration if Java type mapping is known;
    otherwise returns the raw value (e.g., for primitive types).
    """
    if value_type in RAW_TYPES:
        return value

    java_type = META_FIELD_TYPES.get(field_name) or map_value_type_to_java_type(value_type)

    if java_type:
        return {"@type": java_type, "value": value}
    return value
