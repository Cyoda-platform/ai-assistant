"""
UpdateRoutesFileCb25PromptConfig Configuration

Generated from config: workflow_configs/prompts/update_routes_file_cb25/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """You need to check and fix the Controller class.

When writing Spring Boot REST controllers that interact with EntityService:
 Use get_pojo_contents tool to understand the entity data model and available properties

CRITICAL RULES:
- EntityService methods are: getItem(), addItem(), updateItem(), deleteItem() - NOT findItemById() or deleteItemById()
- EntityService methods expect UUID technicalId parameters, not String - always use UUID.fromString(stringId)
- EntityService.getItem() returns ObjectNode - use objectMapper.treeToValue(node, EntityClass.class) to convert to entity
- EntityService.deleteItem() returns UUID (the deleted ID), not boolean
- Add JsonProcessingException to method signatures when using objectMapper.treeToValue()
- Entity technicalId fields are UUID type - use UUID.fromString() when setting from String DTOs
- Map DTO fields correctly to entity fields (check entity class for actual field names)
- Always import: UUID, JsonProcessingException, ObjectNode when using EntityService

VALIDATION CHECKLIST:
□ Method names match com.java_template.common.service.EntityService interface exactly
□ EntityService injected via constructor
□ ObjectMapper injected via constructor
□ UUID conversions applied where needed
□ ObjectMapper used for ObjectNode → Entity conversion
□ Exception handling includes JsonProcessingException
□ DTO → Entity field mapping verified against actual entity classes
□ All required imports present

When managing imports in Spring Boot controllers using EntityService:

REQUIRED IMPORTS CHECKLIST:
□ com.fasterxml.jackson.core.JsonProcessingException (when using objectMapper.treeToValue)
□ com.fasterxml.jackson.databind.ObjectMapper (for JSON operations)
□ com.fasterxml.jackson.databind.node.ObjectNode (EntityService return type)
□ java.util.UUID (for technicalId conversions)
□ java.util.concurrent.ExecutionException (for CompletableFuture.get())
□ jakarta.validation.Valid (for request validation)
□ jakarta.validation.constraints.NotBlank (for field validation)
□ org.springframework.http.ResponseEntity (for REST responses)
□ org.springframework.web.bind.annotation.* (for REST mappings)
□ import static com.java_template.common.config.Config.ENTITY_VERSION

COMMON MISSING IMPORTS:
- JsonProcessingException when using objectMapper.treeToValue()
- UUID when converting String IDs to UUID
- ObjectNode when working with EntityService responses

ADDITIONAL CRITICAL RECOMMENDATIONS:

1. VALIDATION ANNOTATIONS:
✅ Use @jakarta.validation.constraints.* (NOT @javax.validation.constraints.*)
✅ Import: import jakarta.validation.constraints.Email;
❌ Avoid: import javax.validation.constraints.Email;

2. ENTITY SERVICE METHOD SIGNATURES:
✅ addItem(String entityModel, String entityVersion, Object entity) returns CompletableFuture<UUID>
✅ updateItem(String entityModel, String entityVersion, UUID technicalId, Object entity) requires 4 parameters
❌ Don't assume addItem() returns String - it returns UUID
❌ Don't call updateItem() with only 3 parameters - it needs the technicalId

3. ENTITY FIELD MAPPING:
Before calling setter methods on entities, ALWAYS verify the actual field names in the entity class

4. LOMBOK @Data ANNOTATION:
- Entities use @Data annotation which auto-generates getters/setters
- Method names follow JavaBean convention: fieldName → getFieldName() / setFieldName()
- Always check the actual field names in the entity class before calling methods

5. UUID HANDLING:
- Convert UUID to String when needed: uuid.toString()
- Parse String to UUID when needed: UUID.fromString(string)
- EntityService methods return CompletableFuture<UUID>, not CompletableFuture<String>

Response format: respond with only the code. No markdown formatting, no explanation. Regular Java comments (// like this) are allowed, but avoid extra narrative or markdown-style formatting. Do not include code block markers like ```."""
