from enum import Enum

# Operation type mappings
OPERATION_MAPPING = {
    "equals (disregard case)": {
        "operation": "IEQUALS",
        "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals"
    },
    "not equal (disregard case)": {
        "operation": "INOT_EQUAL",
        "@bean": "com.cyoda.core.conditions.nonqueryable.INotEquals"
    },
    "between (inclusive)": {
        "operation": "BETWEEN",
        "@bean": "com.cyoda.core.conditions.queryable.Between"
    },
    "contains": {
        "operation": "CONTAINS",
        "@bean": "com.cyoda.core.conditions.nonqueryable.IContains"
    },
    "starts with": {
        "operation": "ISTARTS_WITH",
        "@bean": "com.cyoda.core.conditions.nonqueryable.IStartsWith"
    },
    "ends with": {
        "operation": "IENDS_WITH",
        "@bean": "com.cyoda.core.conditions.nonqueryable.IEndsWith"
    },
    "does not contain": {
        "operation": "INOT_CONTAINS",
        "@bean": "com.cyoda.core.conditions.nonqueryable.INotContains"
    },
    "does not start with": {
        "operation": "INOT_STARTS_WITH",
        "@bean": "com.cyoda.core.conditions.nonqueryable.INotStartsWith"
    },
    "does not end with": {
        "operation": "NOT_ENDS_WITH",
        "@bean": "com.cyoda.core.conditions.nonqueryable.NotEndsWith"
    },
    "matches other field (case insensitive)": {
        "operation": "INOT_ENDS_WITH",
        "@bean": "com.cyoda.core.conditions.nonqueryable.INotEndsWith"
    },
    "equals": {
        "operation": "EQUALS",
        "@bean": "com.cyoda.core.conditions.queryable.Equals"
    },
    "not equal": {
        "operation": "NOT_EQUAL",
        "@bean": "com.cyoda.core.conditions.nonqueryable.NotEquals"
    },
    "less than": {
        "operation": "LESS_THAN",
        "@bean": "com.cyoda.core.conditions.queryable.LessThan"
    },
    "greater than": {
        "operation": "GREATER_THAN",
        "@bean": "com.cyoda.core.conditions.queryable.GreaterThan"
    },
    "less than or equal to": {
        "operation": "LESS_OR_EQUAL",
        "@bean": "com.cyoda.core.conditions.queryable.LessThanEquals"
    },
    "greater than or equal to": {
        "operation": "GREATER_OR_EQUAL",
        "@bean": "com.cyoda.core.conditions.queryable.GreaterThanEquals"
    },
    "between (inclusive, match case)": {
        "operation": "BETWEEN_INCLUSIVE",
        "@bean": "com.cyoda.core.conditions.queryable.BetweenInclusive"
    },
    "is null": {
        "operation": "IS_NULL",
        "@bean": "com.cyoda.core.conditions.nonqueryable.IsNull"
    },
    "is not null": {
        "operation": "NOT_NULL",
        "@bean": "com.cyoda.core.conditions.nonqueryable.NotNull"
    }
}

# Supported value types
VALID_VALUE_TYPES = {
    "classes", "nulls", "localTimes", "timeuuids", "years", "longs", "yearMonths", "strings",
    "ints", "byteArrays", "booleans", "bigIntegers", "shorts", "typeReferences", "zonedDateTimes",
    "floats", "bigDecimals", "dates", "localDates", "locales", "doubles", "bytes", "localDateTimes",
    "chars", "uuids"
}

# Mapping from abstract types to Java types
VALUE_TYPE_TO_JAVA_TYPE = {
    "strings": "String",
    "uuids": "java.util.UUID",
    "timeuuids": "com.datastax.oss.driver.api.core.uuid.Uuids",
    "dates": "java.util.Date",
    "localDates": "java.time.LocalDate",
    "localTimes": "java.time.LocalTime",
    "localDateTimes": "java.time.LocalDateTime",
    "zonedDateTimes": "java.time.ZonedDateTime",
    "yearMonths": "java.time.YearMonth",
    "years": "java.time.Year",
    "locales": "java.util.Locale",
    "chars": "char",
    "byteArrays": "byte[]",
    "classes": "java.lang.Class",
    "typeReferences": "java.lang.reflect.Type"
}

# Metadata field types for known field names
META_FIELD_TYPES = {
    "id": "UUID",
    "entityModelClassId": "UUID",
    "owner": "String",
    "state": "String",
    "entityModelName": "String",
    "previousTransition": "String",
    "creationDate": "java.util.Date",
    "lastUpdateTime": "java.util.Date",
    "entityModelVersion": None  # intentionally left as None
}

# Set of raw numeric/boolean types that don't need wrapping
RAW_TYPES = {
    "ints", "longs", "doubles", "floats", "booleans", "shorts", "bytes", "bigDecimals", "bigIntegers"
}

# Prefix used to resolve field names from JSONPath
FIELD_NAME_PREFIX = (
    "members.[*]@com#cyoda#tdb#model#treenode#NodeInfo.value@com#cyoda#tdb#model#treenode#PersistedValueMaps."
)


# Enum for transition keys, matching internal Cyoda conventions
class TransitionKey(str, Enum):
    MANUAL_RETRY = "manual_retry"
    FAIL = "fail"
    ROLLBACK = "rollback"
    LOCKED_CHAT = "locked_chat"


# Enum for AI-specific error codes
class AiErrorCodes(str, Enum):
    WRONG_GENERATED_CONTENT = "wrong_generated_content"
