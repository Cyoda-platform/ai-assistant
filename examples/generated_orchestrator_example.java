package com.java_template.application.orchestrator;

import com.cyoda.plugins.mapping.entity.CyodaEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class JobWorkflowOrchestrator {
    
    private static final Logger logger = LoggerFactory.getLogger(JobWorkflowOrchestrator.class);
    
    @Autowired
    private ProcessorsFactory processorsFactory;
    
    @Autowired
    private CriteriaFactory criteriaFactory;
    
    public String run(String technicalId, CyodaEntity entity, String transition) {
        logger.info("Running {} workflow orchestrator for transition: {}", "Job", transition);
        
        String nextTransition = transition;
        
        try {
            if ("validate_and_start_ingesting".equals(transition)) {
                processorsFactory.get("JobValidationProcessor").process(technicalId, entity);
                nextTransition = "ingesting";
            }

            if ("ingest_data_and_save_laureates".equals(transition)) {
                processorsFactory.get("DataIngestionProcessor").process(technicalId, entity);
                if (criteriaFactory.get("IngestionSuccessCriterion").check(technicalId, entity)) {
                    nextTransition = "succeeded";
                } else {
                    nextTransition = "failed";
                }
            }

            if ("ingest_data_failure".equals(transition)) {
                if (criteriaFactory.get("IngestionFailureCriterion").check(technicalId, entity)) {
                    nextTransition = "failed";
                } else {
                    nextTransition = "failed";
                }
            }

            if ("notify_subscribers".equals(transition)) {
                processorsFactory.get("SubscribersNotifierProcessor").process(technicalId, entity);
                nextTransition = "notified_subscribers";
            }
        } catch (Exception e) {
            logger.error("Error processing transition: " + transition, e);
            nextTransition = "error_state";
        }
        
        logger.info("Transition {} resulted in next state: {}", transition, nextTransition);
        return nextTransition;
    }
}
