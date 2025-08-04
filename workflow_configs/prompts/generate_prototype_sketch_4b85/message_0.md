## Task: Generate EntityControllerPrototype.java

Create a Spring Boot REST controller prototype that demonstrates the API design and validates functionality before full implementation.

### 1. DISCOVERY PHASE (MANDATORY)
**You can use the following tools:**
- Use `list_directory_files` to discover all entity classes in 'src/main/java/com/java_template/application/entity'
- Use `read_file` to examine each entity class and understand their fields and structure

### 2. CONTROLLER STRUCTURE
```java
package com.java_template.prototype;

@RestController
@RequestMapping(path = "/prototype")
@Slf4j
public class EntityControllerPrototype {
    // Implementation here
}
```

### 3. REQUIRED IMPORTS
```java
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import lombok.extern.slf4j.Slf4j;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.*;
```

### 4. EVENT-DRIVEN ARCHITECTURE IMPLEMENTATION

**IMPORTANT: EDA/NoSQL Architecture Principles**
- This system follows **append-only, immutable data patterns**
- **NO UPDATE - use versioning
- Avoid deletes unless explicitly required
- Focus on **event creation** rather than data modification

**Cache Structure (for each discovered entity):**
```java
private final ConcurrentHashMap<String, EntityName> entityNameCache = new ConcurrentHashMap<>();
private final AtomicLong entityNameIdCounter = new AtomicLong(1);
```

**Event-Driven Flow Pattern (EDA-Compliant):**
1. **POST /prototype/entityName** → Create entity → Save to cache → Trigger `processEntityName(entity)` → Return response
- If you have an orchestration entity (like Job, Task, Workflow), it should have a POST endpoint to create it, and a GET by technicalId to retrieve it. You will most likely not need any other POST endpoints for business entities as saving business entity is done via the process method.
2. **GET /prototype/entityName/{id}** → Retrieve from cache → Return entity. Each entity should have a GET by technicalId.
3. Only if the user explicitly asked for update: **POST /prototype/entityName/{id}/update** → Create new entity version → Save to cache → Trigger `processEntityName(entity)` → Return response (still avoid unless necessary)
4. Only if the user explicitly asked for delete/deactivate: **POST /prototype/entityName/{id}/deactivate** → Create deactivation record → Save to cache → Return confirmation (still avoid unless necessary)

**CRITICAL: No PUT/PATCH/DELETE endpoints** - use POST for all state changes to maintain event history
 Keep endpoints to the minimum, just POST to register event and get to retrieve information
 Concentrate on process entity methods - fully implement business logic there, including API calls, calculations, etc.
### 5. CRITICAL: processEntityName() METHODS (variation: process{EntityName}{ProcessorName}() - if stated in the functional requirement). There might be multiple processors and criteria (check{EntityName}{CriteriaName}() methods. You should call them one by one after save. If criteria returns true then processor etc) .
**Each entity MUST have a corresponding process method with meaningful business logic:**

```java
private void process{EntityName}(String technicalId, EntityName entity) {
     IMPLEMENT ACTUAL BUSINESS LOGIC HERE
     Examples:
     - Data validation and enrichment
     - External API calls
     - Triggering workflows
     - Creating related entities
     - Sending notifications
    
    Replace with actual business logic from requirements. no todos. here should be real logic.
}
CRITICAL: If the user provides any external API calls, make sure to implement them.
```

### 8. IMPLEMENTATION GUIDELINES
- **Real implementations preferred**: Use actual logic where requirements are clear
- **Logging**: Use `log.info()` for successful operations, `log.error()` for failures
- **ID generation**: Use AtomicLong for simple incremental IDs
- Return appropriate HTTP status codes (200, 201, 400, 404, 500)

**Remember**: This is a working prototype to validate API design and business logic flow. The processEntityName() methods are the core of the event-driven architecture and must contain substantial business logic relevant to your requirements.
Response format: respond with only the code. No markdown formatting, no explanation. Regular Java comments (// like this) are allowed, but avoid extra narrative or markdown-style formatting. Do not include code block markers like ```