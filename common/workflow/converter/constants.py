from common.config.config import config

#todo remove textual keys
OPERATION_MAPPING = {
    "equals (disregard case)": {"operation": "IEQUALS", "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals"},
    "not equal (disregard case)": {"operation": "INOT_EQUAL",
                                   "@bean": "com.cyoda.core.conditions.nonqueryable.INotEquals"},
    "between (inclusive)": {"operation": "BETWEEN", "@bean": "com.cyoda.core.conditions.queryable.Between"},
    "contains": {"operation": "CONTAINS", "@bean": "com.cyoda.core.conditions.nonqueryable.IContains"},
    "starts with": {"operation": "ISTARTS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.IStartsWith"},
    "ends with": {"operation": "IENDS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.IEndsWith"},
    "does not contain": {"operation": "INOT_CONTAINS", "@bean": "com.cyoda.core.conditions.nonqueryable.INotContains"},
    "does not start with": {"operation": "INOT_STARTS_WITH",
                            "@bean": "com.cyoda.core.conditions.nonqueryable.INotStartsWith"},
    "does not end with": {"operation": "NOT_ENDS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.NotEndsWith"},
    "matches other field (case insensitive)": {"operation": "INOT_ENDS_WITH",
                                               "@bean": "com.cyoda.core.conditions.nonqueryable.INotEndsWith"},
    "equals": {"operation": "EQUALS", "@bean": "com.cyoda.core.conditions.queryable.Equals"},
    "not equal": {"operation": "NOT_EQUAL", "@bean": "com.cyoda.core.conditions.nonqueryable.NotEquals"},
    "less than": {"operation": "LESS_THAN", "@bean": "com.cyoda.core.conditions.queryable.LessThan"},
    "greater than": {"operation": "GREATER_THAN", "@bean": "com.cyoda.core.conditions.queryable.GreaterThan"},
    "less than or equal to": {"operation": "LESS_OR_EQUAL",
                              "@bean": "com.cyoda.core.conditions.queryable.LessThanEquals"},
    "greater than or equal to": {"operation": "GREATER_OR_EQUAL",
                                 "@bean": "com.cyoda.core.conditions.queryable.GreaterThanEquals"},
    "between (inclusive, match case)": {"operation": "BETWEEN_INCLUSIVE",
                                        "@bean": "com.cyoda.core.conditions.queryable.BetweenInclusive"},
    "is null": {"operation": "IS_NULL", "@bean": "com.cyoda.core.conditions.nonqueryable.IsNull"},
    "is not null": {"operation": "NOT_NULL", "@bean": "com.cyoda.core.conditions.nonqueryable.NotNull"},
    "IEQUALS": {"operation": "IEQUALS", "@bean": "com.cyoda.core.conditions.nonqueryable.IEquals"},
    "INOT_EQUAL": {"operation": "INOT_EQUAL",
                                   "@bean": "com.cyoda.core.conditions.nonqueryable.INotEquals"},
    "BETWEEN": {"operation": "BETWEEN", "@bean": "com.cyoda.core.conditions.queryable.Between"},
    "CONTAINS": {"operation": "CONTAINS", "@bean": "com.cyoda.core.conditions.nonqueryable.IContains"},
    "ISTARTS_WITH": {"operation": "ISTARTS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.IStartsWith"},
    "IENDS_WITH": {"operation": "IENDS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.IEndsWith"},
    "INOT_CONTAINS": {"operation": "INOT_CONTAINS", "@bean": "com.cyoda.core.conditions.nonqueryable.INotContains"},
    "INOT_STARTS_WITH": {"operation": "INOT_STARTS_WITH",
                            "@bean": "com.cyoda.core.conditions.nonqueryable.INotStartsWith"},
    "NOT_ENDS_WITH": {"operation": "NOT_ENDS_WITH", "@bean": "com.cyoda.core.conditions.nonqueryable.NotEndsWith"},
    "INOT_ENDS_WITH": {"operation": "INOT_ENDS_WITH",
                                               "@bean": "com.cyoda.core.conditions.nonqueryable.INotEndsWith"},
    "EQUALS": {"operation": "EQUALS", "@bean": "com.cyoda.core.conditions.queryable.Equals"},
    "NOT_EQUAL": {"operation": "NOT_EQUAL", "@bean": "com.cyoda.core.conditions.nonqueryable.NotEquals"},
    "LESS_THAN": {"operation": "LESS_THAN", "@bean": "com.cyoda.core.conditions.queryable.LessThan"},
    "GREATER_THAN": {"operation": "GREATER_THAN", "@bean": "com.cyoda.core.conditions.queryable.GreaterThan"},
    "LESS_OR_EQUAL": {"operation": "LESS_OR_EQUAL",
                              "@bean": "com.cyoda.core.conditions.queryable.LessThanEquals"},
    "GREATER_OR_EQUAL": {"operation": "GREATER_OR_EQUAL",
                                 "@bean": "com.cyoda.core.conditions.queryable.GreaterThanEquals"},
    "BETWEEN_INCLUSIVE": {"operation": "BETWEEN_INCLUSIVE",
                                        "@bean": "com.cyoda.core.conditions.queryable.BetweenInclusive"},
    "IS_NULL": {"operation": "IS_NULL", "@bean": "com.cyoda.core.conditions.nonqueryable.IsNull"},
    "NOT_NULL": {"operation": "NOT_NULL", "@bean": "com.cyoda.core.conditions.nonqueryable.NotNull"},

}

VALID_VALUE_TYPES = {
    "classes", "nulls", "localTimes", "timeuuids", "years", "longs", "yearMonths", "strings",
    "ints", "byteArrays", "booleans", "bigIntegers", "shorts", "typeReferences", "zonedDateTimes",
    "floats", "bigDecimals", "dates", "localDates", "locales", "doubles", "bytes", "localDateTimes",
    "chars", "uuids"
}

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
    "typeReferences": "java.lang.reflect.Type",
}

META_FIELD_TYPES = {
    "id": "UUID",
    "entityModelClassId": "UUID",
    "owner": "String",
    "state": "String",
    "entityModelName": "String",
    "previousTransition": "String",
    "creationDate": "java.util.Date",
    "lastUpdateTime": "java.util.Date",
    "entityModelVersion": None
}

RAW_TYPES = {
    "ints", "longs", "doubles", "floats", "booleans", "shorts", "bytes", "bigDecimals", "bigIntegers"
}

FIELD_NAME_PREFIX = (
    "members.[*]@com#cyoda#tdb#model#treenode#NodeInfo.value@com#cyoda#tdb#model#treenode#PersistedValueMaps."
)
DEFAULT_PARAM_VALUES = {
    "owner": "CYODA",
    "user": "CYODA",
    "attach_entity": "true",
    "calculation_response_timeout_ms": "300000",
    "retry_policy": "FIXED",  # NONE
    "sync_process": "false",
    "new_transaction_for_async": "true",
    "none_transactional_for_async": "false",
    "default_condition_name": "default_condition_name",
    "calculation_nodes_tags": config.GRPC_PROCESSOR_TAG
}