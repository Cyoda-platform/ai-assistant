"""
ExtractEntitiesFromPrototypeE7faPromptConfig Configuration

Generated from config: workflow_configs/prompts/extract_entities_from_prototype_e7fa/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None:\
"""You are provided with the requirements document.

Your task:
- Identify entities from the requirements document.
- Min 1 entity, Max 3 entities unless explicitly asked for more:
  - Orchestration entities (e.g. 'Job', 'Task') take precedence.
  - After orchestration entities, identify business domain entities.
  - There can only be one orchestration entity.
- You must call add_application_resource at least once.

For each identified entity, call add_application_resource with:
- resource_path: 'src/main/java/com/java_template/application/entity/{EntityName}.java'
- file_contents: entity Java POJO using Lombok @Data annotation.

Use the following entity class template (replace EntityName with the actual entity name):

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

Rules:
- Replace "EntityName" with the actual entity class name (PascalCase).
- Add appropriate fields based on the prototype code.
- Implement proper validation logic in isValid() (e.g., use .isBlank() for String fields, not null checks for UUID fields).
- If enums are needed, use String instead.
- Ensure @Data from Lombok generates all required getters/setters.
- POST endpoints that add entities should return only a technical id.
- Use String types for foreign key references representing serialized UUIDs.
- Ensure add_application_resource is called at least once.

Requirement:"""
