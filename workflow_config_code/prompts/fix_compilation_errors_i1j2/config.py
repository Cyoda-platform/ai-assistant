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

    // Retrieve a single item based on its ID.
    CompletableFuture<DataPayload> getItem(@NotNull UUID entityId);

    // Retrieve an item based on a condition.
    CompletableFuture<Optional<DataPayload>> getFirstItemByCondition(
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull Object condition,
            boolean inMemory
    );

    // Retrieve multiple items based on the entity model and version.
    CompletableFuture<List<DataPayload>> getItems(
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @Nullable Integer pageSize,
            @Nullable Integer pageNumber,
            @Nullable Date pointTime
    );

    // Retrieve items based on a condition with option for in-memory search.
    CompletableFuture<List<DataPayload>> getItemsByCondition(
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull Object condition,
            boolean inMemory
    );

    // Add a new item to the repository and return the entity's unique ID.
    <ENTITY_TYPE> CompletableFuture<UUID> addItem(
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull ENTITY_TYPE entity
    );

    // Add a new item to the repository and return the entity ID along with the
    // transaction ID.
    <ENTITY_TYPE> CompletableFuture<ObjectNode> addItemAndReturnTransactionInfo(
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull ENTITY_TYPE entity
    );

    // Add a list of items to the repository and return the entities' IDs.
    <ENTITY_TYPE> CompletableFuture<List<UUID>> addItems(
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull Collection<ENTITY_TYPE> entities
    );

    // Add a list of items to the repository and return the entities' IDs along with
    // the transaction ID.
    <ENTITY_TYPE> CompletableFuture<EntityTransactionInfo> addItemsAndReturnTransactionInfo(
            @NotNull String modelName,
            @NotNull Integer modelVersion,
            @NotNull Collection<ENTITY_TYPE> entities
    );

    // Update an existing item in the repository.
    <ENTITY_TYPE> CompletableFuture<UUID> updateItem(@NotNull UUID entityId, @NotNull ENTITY_TYPE entity);

    <ENTITY_TYPE> CompletableFuture<List<UUID>> updateItems(@NotNull Collection<ENTITY_TYPE> entities);

    CompletableFuture<List<String>> applyTransition(@NotNull UUID entityId, @NotNull String transitionName);

    // Delete an item by ID.
    CompletableFuture<UUID> deleteItem(@NotNull UUID entityId);

    // Delete all items by modelName and modelVersion.
    CompletableFuture<Integer> deleteItems(@NotNull String modelName, @NotNull Integer modelVersion);
}

This is how we setup ObjectMapper:
ObjectMapper objectMapper = new ObjectMapper();
// Configure ObjectMapper to ignore unknown properties during deserialization
objectMapper.configure(com.fasterxml.jackson.databind.DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        
===================

Output format:
Return only the full Java code without any additional text or comments.
"""
