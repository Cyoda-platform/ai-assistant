"""
FixCompilationErrorsI1j2PromptConfig Configuration

Configuration data for the fix compilation errors prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
You are tasked with fixing compilation errors for a specific Java file. You will receive the file path and have access to both the source file and the compilation output JSON.

INPUT:
- A specific Java file path that has compilation errors
- project_compilation_output.json contains the error details for this file

EXECUTION WORKFLOW - FOLLOW EXACTLY:

PHASE 1: ANALYZE FILE-SPECIFIC ERRORS
1. Read the project_compilation_output.json to find errors for this specific file
2. Extract the specific error messages for the current file
3. Read the source file to understand the current code structure

PHASE 2: IDENTIFY AND FIX ERRORS
4. For the current file, analyze each compilation error:
   - Understand the root cause of each error
   - Apply appropriate fixes:
     * Missing imports
     * Incorrect package declarations
     * Syntax errors
     * Type mismatches
     * Missing method implementations
     * Incorrect annotations
     * Dependency issues

PHASE 3: SAVE CORRECTED FILE
5. Write the corrected Java file content directly to the output path
   - Ensure all compilation errors for this file are fixed
   - Maintain proper Java coding standards and conventions
   - Preserve existing functionality while fixing errors

CRITICAL CONSTRAINTS:
🚨 Only fix compilation errors identified in the JSON for this specific file
🚨 Preserve existing functionality while fixing errors
🚨 Maintain proper Java coding standards and conventions
🚨 Ensure all imports are correct and necessary
🚨 Verify package declarations match directory structure
🚨 Test logical consistency of fixes before applying

COMMON COMPILATION ERROR PATTERNS TO LOOK FOR:
- Missing import statements
- Incorrect package declarations
- Undefined variables or methods
- Type casting issues
- Missing semicolons or brackets
- Incorrect annotation usage
- Interface implementation issues
- Generic type problems
- Access modifier conflicts

Your task is complete when you have:
1. ✅ Analyzed the compilation errors for this specific file
2. ✅ Fixed all identified compilation errors in the Java file
4. ✅ Ensured all fixes maintain code quality and functionality

===================
Reference:

This is the org.cyoda.cloud.api.event.common.DataPayload class:
public class DataPayload {

    @JsonProperty("data")
    public JsonNode getData() {
        return data;
    }
    @JsonProperty("meta")
    public JsonNode getMeta() {
        return meta;
    }
}

This is com.java_template.common.service.EntityService class:

package com.java_template.common.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.java_template.application.entity.adoptionrequest.version_1.AdoptionRequest;
import com.java_template.common.serializer.CriterionSerializer;
import com.java_template.common.serializer.ProcessorSerializer;
import com.java_template.common.serializer.SerializerFactory;
import com.java_template.common.serializer.jackson.JacksonCriterionSerializer;
import com.java_template.common.serializer.jackson.JacksonProcessorSerializer;
import com.java_template.common.service.EntityService;
import com.java_template.common.workflow.CyodaEventContext;
import org.cyoda.cloud.api.event.common.DataPayload;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationRequest;
import org.cyoda.cloud.api.event.processing.EntityProcessorCalculationResponse;
import org.junit.jupiter.api.Test;


public interface EntityService {

    // Core retrieval methods - all synchronous for consistency

    // Retrieve a single item based on its ID with metadata
    <T extends CyodaEntity> EntityResponse<T> getItem(
            @NotNull UUID entityId,
            @NotNull Class<T> entityClass
    );

    // Retrieve an item based on a condition with metadata
    <T extends CyodaEntity> Optional<EntityResponse<T>> getFirstItemByCondition(
            @NotNull Class<T> entityClass,
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull SearchConditionRequest condition,
            boolean inMemory
    );

    // Retrieve multiple items based on the entity model and version with metadata
    <T extends CyodaEntity> List<EntityResponse<T>> getItems(
            @NotNull Class<T> entityClass,
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @Nullable Integer pageSize,
            @Nullable Integer pageNumber,
            @Nullable Date pointTime
    );

    // Retrieve items based on a condition with option for in-memory search with metadata
    <T extends CyodaEntity> List<EntityResponse<T>> getItemsByCondition(
            @NotNull Class<T> entityClass,
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull SearchConditionRequest condition,
            boolean inMemory
    );

    // Mutation methods - Spring Boot JPA style naming, all synchronous

    // Save a new entity and return with full metadata (JPA style)
    <T extends CyodaEntity> EntityResponse<T> save(@NotNull T entity);

    // Save a new entity and return transaction info (for advanced use cases)
    <T extends CyodaEntity> ObjectNode saveAndReturnTransactionInfo(@NotNull T entity);

    // Save multiple entities and return with metadata (JPA style)
    <T extends CyodaEntity> List<EntityResponse<T>> saveAll(@NotNull Collection<T> entities);

    // Save multiple entities and return transaction info (for advanced use cases)
    <T extends CyodaEntity> EntityTransactionInfo saveAllAndReturnTransactionInfo(@NotNull Collection<T> entities);

    // Update an existing entity with optional transition and return with metadata
    <T extends CyodaEntity> EntityResponse<T> update(@NotNull UUID entityId, @NotNull T entity, @Nullable String transition);

    // Update multiple entities with optional transition and return with metadata
    <T extends CyodaEntity> List<EntityResponse<T>> updateAll(@NotNull Collection<T> entities, @Nullable String transition);

    // Delete operations (JPA style naming)
    UUID deleteById(@NotNull UUID entityId);

    Integer deleteAll(@NotNull String modelName, @NotNull Integer modelVersion);

    // High-level convenience methods - business ID based operations

    // Find entity by business ID with metadata
    <T extends CyodaEntity> EntityResponse<T> findByBusinessId(@NotNull Class<T> entityClass, @NotNull String modelName, @NotNull Integer modelVersion, @NotNull String businessId, @NotNull String businessIdField);

    // Find all entities with metadata (JPA style)
    <T extends CyodaEntity> List<EntityResponse<T>> findAll(@NotNull Class<T> entityClass, @NotNull String modelName, @NotNull Integer modelVersion);

    // Update an entity by business ID with optional transition
    <T extends CyodaEntity> EntityResponse<T> updateByBusinessId(@NotNull T entity, @NotNull String businessIdField, @Nullable String transition);

    // Delete entity by business ID
    boolean deleteByBusinessId(@NotNull String modelName, @NotNull Integer modelVersion, @NotNull String businessId, @NotNull String businessIdField);

    // Find entities by field value with metadata (convenience method)
    <T extends CyodaEntity> List<EntityResponse<T>> findByField(@NotNull Class<T> entityClass, @NotNull String modelName, @NotNull Integer modelVersion, @NotNull String fieldName, @NotNull String value);

    // Find entities by search condition with metadata (advanced search)
    <T extends CyodaEntity> List<EntityResponse<T>> findByCondition(@NotNull Class<T> entityClass, @NotNull String modelName, @NotNull Integer modelVersion, @NotNull SearchConditionRequest condition, boolean inMemory);

    // Convenience methods for backward compatibility - extract data from EntityResponse

    // Get just the business data (for backward compatibility)
    default <T extends CyodaEntity> T getData(EntityResponse<T> response) {
        return response.getData();
    }

    // Get just the business data list (for backward compatibility)
    default <T extends CyodaEntity> List<T> getData(List<EntityResponse<T>> responses) {
        return responses.stream().map(EntityResponse::getData).toList();
    }
}

    record ProcessorEntityExecutionContext<T extends CyodaEntity>(EntityProcessorCalculationRequest request, T entity) {}
    record ProcessorExecutionContext(EntityProcessorCalculationRequest request, JsonNode payload) {}

CRITICAL: Never use Java reflection. Use entity getters and setters only. If there are settings of non-existent properties in the entity, just remove them.
CRITICAL: Never use Java reflection. Use entity getters and setters only. If there's code accessing non-existent properties in the entity, just remove this code from the processor.

This is how we setup ObjectMapper:
ObjectMapper objectMapper = new ObjectMapper();
// Configure ObjectMapper to ignore unknown properties during deserialization
objectMapper.configure(com.fasterxml.jackson.databind.DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        
===================

Output format:
Return only the full Java code without any additional text or comments.
"""
