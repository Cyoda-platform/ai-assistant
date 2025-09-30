You are given a Gradle-based Java project with workflow “processors” that implement the interface:
com.java_template.common.workflow.CyodaProcessor
Method signature: EntityProcessorCalculationResponse process(CyodaEventContext context)
Your task: write one JUnit 5 test class
==
Requirements:
Exactly one “sunny day” scenario test for processor class (one @Test method per class)
Only mock EntityService when needed; do not mock anything else
Use real Jackson serializers and a real SerializerFactory (no Spring context)
Do not introduce new test dependencies beyond JUnit 5 and Mockito already available
Do not use Spring test runners or ApplicationContext
Serializer setup (use real objects):
This is how we setup ObjectMapper:
ObjectMapper objectMapper = new ObjectMapper();
// Configure ObjectMapper to ignore unknown properties during deserialization
objectMapper.configure(com.fasterxml.jackson.databind.DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        
ProcessorSerializer = new JacksonProcessorSerializer(objectMapper)
CriterionSerializer = new JacksonCriterionSerializer(objectMapper)
SerializerFactory serializerFactory = new SerializerFactory(
                java.util.List.of(processorSerializer),
                java.util.List.of(criterionSerializer)
        );
Context setup (no Spring):
Build EntityProcessorCalculationRequest with:
id, requestId, entityId, processorName
DataPayload payload = new DataPayload(); payload.setData(objectNodePayload); request.setPayload(payload);
Provide a minimal CyodaEventContext via an anonymous class:
getCloudEvent() returns null
getEvent() returns the request
Mocking policy:
Only EntityService may be mocked (when present in processor constructor)
For processors whose constructor requires EntityService, pass a Mockito mock
For sunny day paths requiring EntityService calls (e.g., getItemsByCondition), stub minimal return values
Payloads and validation:
Processors call serializer.withRequest(...).toEntity(...).validate(entity::isValid,...)
Ensure your JSON payload is sufficient for entity.isValid() to pass for the entity type used:
Tailor payload fields based on what processor expects in its sunny path
Assertions:
Call processor.process(context) and assert:
response != null
response.getSuccess() is true
Inspect response.getPayload().getData() for the expected sunny-day state changes (e.g., fields set/updated by the processor)
Keep assertions focused and minimal to the processor’s core happy-path behavior

Acceptance criteria:
One and only one @Test test, testing the sunny-day path
Only EntityService is mocked where needed; everything else uses real objects
No Spring context usage in tests

You can use the following code as a reference (it is just an example):
package com.java_template.application.processor;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.java_template.application.entity.entity_name.version_1.EntityName;
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

import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

public class ExampleProcessorTest {

    @Test
    void sunnyDay_process_test() {
        // Arrange
        ObjectMapper objectMapper = new ObjectMapper();
        ProcessorSerializer processorSerializer = new JacksonProcessorSerializer(objectMapper);
        CriterionSerializer criterionSerializer = new JacksonCriterionSerializer(objectMapper);
        SerializerFactory serializerFactory = new SerializerFactory(
                java.util.List.of(processorSerializer),
                java.util.List.of(criterionSerializer)
        );

        EntityService entityService = mock(EntityService.class);
        when(entityService.getItemsByCondition(anyString(), anyString(), any(), anyBoolean()))
                .thenReturn(CompletableFuture.completedFuture(objectMapper.createArrayNode()));
        Check what dependencies the processor has and add them to the processor constructor
        ExampleProcessor processor = new ExampleProcessor(serializerFactory, entityService, objectMapper); // you might not need all of these arguments - check the processor code
        //You MUST use the entity directly, do not use the JsonNode/ObjectNode
        EntityName exampleEntity = new EntityName();
        exampleEntity.setExampleField("exampleValue");
        //Ideally this data should pass the processor isValidEntity validation

        JsonNode entityJson = objectMapper.valueToTree(exampleEntity);

        EntityProcessorCalculationRequest request = new EntityProcessorCalculationRequest();
        request.setId("r1");
        request.setRequestId("r1");
        request.setEntityId("e1");
        request.setProcessorName("ExampleProcessor");
        DataPayload payload = new DataPayload();
        payload.setData(entityJson); //only set data, no other fields
        //data payload has only data and meta (JsonNode) no other fields!
        request.setPayload(payload);

        CyodaEventContext<EntityProcessorCalculationRequest> context = new CyodaEventContext<>() {
            @Override
            public io.cloudevents.v1.proto.CloudEvent getCloudEvent() { return null; }
            @Override
            public EntityProcessorCalculationRequest getEvent() { return request; }
        };

        // Act
        EntityProcessorCalculationResponse response = processor.process(context);

        // Assert
        assertNotNull(response);
        assertTrue(response.getSuccess());
        // Verify EntityService was called for deduplication search
        verify(entityService, atLeastOnce()).addItem(eq("EntityName"), anyString(), any());
    }
}

Reference:
This is the DataPayload class:
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
This is EntityService class:
package com.java_template.common.service;

import java.util.Collection;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

import com.fasterxml.jackson.databind.node.ObjectNode;

import jakarta.annotation.Nullable;
import jakarta.validation.constraints.NotNull;
import org.cyoda.cloud.api.event.common.DataPayload;
import org.cyoda.cloud.api.event.entity.EntityTransactionInfo;

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

Output format:
CRITICAL: Return only the full processor code. Do not include any other text or explanations.