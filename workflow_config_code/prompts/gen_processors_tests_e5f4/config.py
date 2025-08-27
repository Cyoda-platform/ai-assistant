"""
GenProcessorsTestsE5f4 Configuration

Configuration data for the enhance processors prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """
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
new ObjectMapper()
ProcessorSerializer = new JacksonProcessorSerializer(objectMapper)
CriterionSerializer = new JacksonCriterionSerializer(objectMapper)
SerializerFactory serializerFactory = new SerializerFactory( List.of(processorSerializer), List.of(criterionSerializer) )
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

Example skeleton (replace CLASS and payload specifics per processor):
Use this as a guide; keep exactly one @Test per processor
Test skeleton:
Arrange
ObjectMapper om = new ObjectMapper()
ProcessorSerializer ps = new JacksonProcessorSerializer(om)
CriterionSerializer cs = new JacksonCriterionSerializer(om)
SerializerFactory sf = new SerializerFactory(List.of(ps), List.of(cs))
EntityService es = mock(EntityService.class) if constructor needs it
Processor underTest = new CLASS(sf, es?, om?)
ObjectNode data = om.createObjectNode(); // fill fields to satisfy entity.isValid()
DataPayload payload = new DataPayload(); payload.setData(data)
EntityProcessorCalculationRequest req = new EntityProcessorCalculationRequest()
set id/requestId/entityId
set processorName to the actual processor class simple name
setPayload(payload)
CyodaEventContext ctx = new CyodaEventContext<>() { getCloudEvent() => null; getEvent() => req; }
Act
EntityProcessorCalculationResponse resp = underTest.process(ctx)
Assert
assertNotNull(resp); assertTrue(resp.getSuccess())
JsonNode out = resp.getPayload().getData()
assert expected business field(s)
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

        ExampleProcessor processor = new ExampleProcessor(serializerFactory, entityService, objectMapper);
        //You MUST use the entity directly, do not use the JsonNode
        EntityName exampleEntity = new EntityName();
        exampleEntity.setExampleField("exampleValue");

        JsonNode entityJson = objectMapper.valueToTree(exampleEntity);

        EntityProcessorCalculationRequest request = new EntityProcessorCalculationRequest();
        request.setId("r1");
        request.setRequestId("r1");
        request.setEntityId("e1");
        request.setProcessorName("ExampleProcessor");
        DataPayload payload = new DataPayload();
        payload.setData(entityJson);
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

Output format:
CRITICAL: Return only the full processor code. Do not include any other text or explanations.
"""
