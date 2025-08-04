You are provided with the requirements document.

You need to identify entities from the requirements document.
Min 1 entity, Max 3 entities: orchestration entities like 'Job', 'Task' take precedence, then business domain entities.
 There can be only one orchestration entity. But you should call add_application_resource at least once
For each entity, call add_application_resource with:
- resource_path: 'src/main/java/com/java_template/application/entity/{EntityName}.java'
- file_contents: entity java pojo with lombok @Data annotation

Use this entity class template (replace EntityName with your actual entity name):

package com.java_template.application.entity;

import com.java_template.common.workflow.CyodaEntity;
import com.java_template.common.workflow.OperationSpecification;
import org.cyoda.cloud.api.event.common.ModelSpec;
import lombok.Data;
import static com.java_template.common.config.Config.ENTITY_VERSION;

@Data
public class EntityName implements CyodaEntity {
    public static final String ENTITY_NAME = "EntityName";
    // Add your entity fields here

    public EntityName() {}

    @Override
    public OperationSpecification getModelKey() {
        ModelSpec modelSpec = new ModelSpec();
        modelSpec.setName(ENTITY_NAME);
        modelSpec.setVersion(Integer.parseInt(ENTITY_VERSION));
        return new OperationSpecification.Entity(modelSpec, ENTITY_NAME);
    }

    @Override
    public boolean isValid() {
        return true;
    }
}

Replace:
- EntityName with your actual entity class name (PascalCase)
- Add appropriate fields based on the prototype code
- Implement proper validation logic in isValid() method

It should be a single class, no nested classes or enum. If there is necessity to use enum - use string instead.
When creating entity classes that implement CyodaEntity:
1.

POST endpoints that add entities should return only technical id. Nothing else.
Use String types for foreign key references when they represent serialized UUIDs
4. 
Update validation logic to match the actual field types (use .isBlank() for String fields, not null checks for UUID fields)

5. Ensure @Data annotation from Lombok generates all necessary getters/setters
 CRITICAL: add_application_resource should be called at least once.
Requirement: