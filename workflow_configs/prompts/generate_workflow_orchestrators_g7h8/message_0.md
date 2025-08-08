
You are tasked with reading workflow JSON files from a directory and generating Java workflow orchestrators.

Your tasks:
1. Read all {EntityName}.json files from the provided workflow directory path parameter
2. Parse each workflow JSON structure (states, transitions, processors, criteria)
3. Generate a Java workflow orchestrator class for each workflow
4. Implement conditional logic based on transitions, processors, and criteria

For each workflow JSON file found, create a Java orchestrator using add_application_resource with:
- resource_path: 'src/main/java/com/java_template/application/orchestrator/{EntityName}WorkflowOrchestrator.java'
- file_contents: complete Java orchestrator class

Java Orchestrator Template:
```java
package com.java_template.application.orchestrator;

import com.java_template.common.workflow.CyodaEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class {EntityName}WorkflowOrchestrator {

    private static final Logger logger = LoggerFactory.getLogger({EntityName}WorkflowOrchestrator.class);

    @Autowired
    private ProcessorsFactory processorsFactory;

    @Autowired
    private CriteriaFactory criteriaFactory;

    public String run(String technicalId, CyodaEntity entity, String transition) {
        logger.info("Running {EntityName} workflow orchestrator for transition: {}", transition);

        String nextTransition = transition;

        // Generated conditional logic based on workflow JSON structure
        if ("transition_name_from_json".equals(transition)) {
            try {
                // Execute processors if defined in transition
                if (hasProcessors) {
                    processorsFactory.get("ProcessorNameFromJson").process(technicalId, entity);
                }

                // Check criteria if defined in transition
                if (hasCriteria) {
                    if (criteriaFactory.get("CriteriaNameFromJson").check(technicalId, entity)) {
                        nextTransition = "success_next_state_from_json";
                    } else {
                        nextTransition = "failure_next_state_from_json";
                    }
                } else {
                    nextTransition = "next_state_from_json";
                }
            } catch (Exception e) {
                logger.error("Error processing transition: " + transition, e);
                nextTransition = "error_state";
            }
        }

        // Generate similar blocks for each transition in the workflow JSON

        return nextTransition;
    }
}
```

Parsing Logic:
1. For each workflow JSON file:
   - Extract entity name from filename (e.g., "Job.json" → "Job")
   - Parse the "states" object to get all states and their transitions

2. For each state in the workflow JSON:
   - For each transition in the state:
     - Create if block: if ("transition_name".equals(transition))
     - If transition has "processors" array:
       * For each processor: processorsFactory.get("ProcessorName").process(technicalId, entity)
     - If transition has "criterion" object:
       * Extract criterion function name
       * Add conditional: if (criteriaFactory.get("CriterionName").check(technicalId, entity))
       * Set nextTransition to transition's "next" value for success case
       * Handle failure case if multiple transitions exist with same criterion
     - If no criterion: set nextTransition to transition's "next" value
     - Handle manual transitions (manual: true) appropriately

3. Generate comprehensive conditional logic covering all workflow paths

4. Include proper error handling, logging, and exception management

5. Use the exact processor and criterion names from the JSON

Example JSON structure to parse:
```json
{
  "states": {
    "scheduled": {
      "transitions": [
        {
          "name": "validate_and_start_ingesting",
          "next": "ingesting",
          "processors": [{"name": "JobValidationProcessor"}]
        }
      ]
    },
    "ingesting": {
      "transitions": [
        {
          "name": "ingest_data_and_save_laureates",
          "next": "succeeded",
          "criterion": {"function": {"name": "IngestionSuccessCriterion"}},
          "processors": [{"name": "DataIngestionProcessor"}]
        },
        {
          "name": "ingest_data_failure",
          "next": "failed",
          "criterion": {"function": {"name": "IngestionFailureCriterion"}}
        }
      ]
    }
  }
}
```

Generate orchestrators for all workflow JSON files found in the directory.
