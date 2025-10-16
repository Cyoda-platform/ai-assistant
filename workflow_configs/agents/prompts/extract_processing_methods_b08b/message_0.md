You need to extract processing methods from Controller.java and create workflow prototypes for each entity.
- Use `list_directory_files` to discover all entity names

Your tasks:
1. Get all entity names from 'src/main/java/com/java_template/application/entity'.
1. Read the Controller.java file contents
2. Identify all process methods (methods that start with 'process' followed by an entity name or some variation of this pattern. these methods are right after putting entity to cache/ 'saving')
3. For each processEntityName method found:
   - Extract the complete method including its body
   - Extract any private helper methods that are directly called by this process method
   - Save the extracted method(s) to 'src/main/java/com/java_template/application/workflow_prototypes/{EntityName}.txt' using add_application_resource
   - If there is no process{EntityName} method found, create a file with a todo to implement business logic later.
4. Return a cleaned version of Controller.java that:
   - Removes all processEntityName methods and their direct helper methods
   - Keeps all other functionality intact (CRUD operations, endpoints, etc.)

Important guidelines:
- Only extract methods that follow the pattern process{EntityName}/process}EntityName}{Something} (e.g., processUser, processUserScheduler) and run{ProcessorName}. run methods should be appended to the related EntityName.txt file.
- Save the extracted methods to 'src/main/java/com/java_template/application/workflow_prototypes/{EntityName}.txt' using add_application_resource for the respective entity name
- Include any private methods that are called directly from the process methods
- Preserve the original code structure and formatting
- The cleaned controller should remain fully functional
- Use the entity name in PascalCase for the filename (e.g., User.txt)

Start by reading the Controller.java file to analyze its structure.
Response format: respond with only the java code. No markdown formatting, no explanation. Regular Java comments (// like this) are allowed, but avoid extra narrative or markdown-style formatting. Do not include code block markers like ```