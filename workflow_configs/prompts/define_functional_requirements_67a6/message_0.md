Please help me define the functional requirements for my project using an Event-Driven Architecture (EDA) approach.

## IMPORTANT EDA CONCEPTS:
In Event-Driven Architecture:
- Each entity add operation is an **EVENT** that triggers automated processing
Once an entity is persisted, Cyoda starts entity workflow that will involve calling actions and criteria to process this entity.
For example, when a Job entity is persisted, Cyoda starts the Job workflow that will involve calling actions and criteria to process this job (ingestion, transformation, etc.)
- Focus on business entities, job entities, or orchestration entities that represent your domain
- **Key Pattern**: Entity persistence triggers the process method that does the heavy lifting

## RESPONSE STRUCTURE:
**Start your answer with outlining the entities and their fields in this format:**

Max 10 entities allowed. If the user specifies more than 10 entities, you should only consider the first 10 will be considered and notify the user.
If the user explicitly specifies less than 10 entities, you should consider only those entities. Do not add any additional entities.
If the user doesn't explicitly specify any entities, default to max 3 entities unless the user explicitly asks for more.

IMPORTANT:
Do your best to represent the user's requirement in the form of entities and their workflows.
Make the workflows represent the business domain as best as possible, adding different states the entity can go through. 
For example Pizza workflow can go through different states: Ordered, Prepared, Delivered, etc.

Make workflows interesting and simulate the real world as best as possible.
 
### 1. Entity Definitions
```
EntityName:
- field1: DataType (description/purpose)
- field2: DataType (description/purpose)
 Do not use enum - not supported temporarily.
```

### 2. Entity workflows
**Continue with explaining the basic flow of each entity:**

**Example:**
```
Job workflow:
1. Initial State: Job created with PENDING status
2. Validation: Check job parameters and data sources
3. Processing: Execute data ingestion/transformation
4. Completion: Update status to COMPLETED/FAILED
5. Notification: Send results to configured endpoints
```
For each entity, include a state diagram:
```mermaid
Entity state diagrams
```

## REQUIREMENTS TO DEFINE:

### 1. Business Entities (Min 1)
- **Orchestration entities** (Job, Task, Workflow) - perfect for scenarios like data ingestion, transformation, aggregation, etl, scheduling, monitoring, etc.
- **Business domain entities** (Order, Customer, Product) - perfect for scenarios like e-commerce, inventory management, etc. 

### 2. API Endpoints Design Rules
- **POST endpoints**: Entity creation (triggers events) + business logic. POST endpoint that adds an entity should return only entity `technicalId` - this field is not included in the entity itself, it's a datastore imitated specific field. Nothing else.
- **GET endpoints**: ONLY for retrieving stored application results
- **GET by technicalId**: ONLY for retrieving stored application results by technicalId - should be present for all entities that are created via POST endpoints.
- **GET by condition**: ONLY for retrieving stored application results by non-technicalId fields - should be present only if explicitly asked by the user.
- **GET all: optional.

- If you have an orchestration entity (like Job, Task, Workflow), it should have a POST endpoint to create it, and a GET by technicalId to retrieve it. You will most likely not need any other POST endpoints for business entities as saving business entity is done via the process method.
- **Business logic rule**: External data sources, calculations, processing → POST endpoints

### 4. Request/Response Formats
Specify JSON structures for all API endpoints.
Visualize request/response formats using Mermaid diagrams.

## VISUAL REPRESENTATION:
Mermaid diagrams rules:
    1. Always start with ```mermaid and close with ``` on a new line.
    2. Do NOT chain multiple arrows on one line. Write each connection separately.
    3. Wrap node labels in double quotes.
    4. Escape special characters in labels (use &#39; for single quotes).
    5. Use 
 for manual line breaks in long labels if needed.
    6. Ensure node IDs only contain letters, numbers, or underscores.
    7. Output only valid Mermaid code inside the code block, no extra text
- Ensure all Mermaid blocks are properly closed

At the end of the response, please include the following message:
**Please review the generated entities and workflows. If you need any changes, please let me know. Feel free to click Approve if this requirement meets your expectations or if you are ready to proceed.**
