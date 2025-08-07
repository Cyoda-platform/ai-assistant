Please, adjust the functional requirements, entities and workflows and the API according to the user request. 
Use 'list_directory_files' tool to list all the files in the project. 
List all files in 'src/main/java/com/java_template/application/entity' to get the list of entities.
List all files in 'src/main/java/com/java_template/application/workflow' to get the list of workflows.

Use 'read_file' tool to read the content of any file. Pass the full path to the file as the parameter.
Application prototype code is available in 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java' file.

Use 'add_application_resource' tool to modify any file, passing the full path to the file and the full content of the file as the second parameter.
Pass resource_path as the first parameter and file_contents as the second parameter.
Resource path for the entities: 'src/main/java/com/java_template/application/entity/{EntityName}.java'
Resource path for the workflows: 'src/main/java/com/java_template/application/workflow/{EntityName}.json'
Resource path for the prototype: 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java'

Use 'add_application_resource' tool to add any new entity or workflow file, passing the full path to the file and the full content of the file as the second parameter.
Pass resource_path as the first parameter and file_contents as the second parameter.
Resource path for the entities: 'src/main/java/com/java_template/application/entity/{EntityName}.java'
Resource path for the workflows: 'src/main/java/com/java_template/application/workflow/{EntityName}.json'
Resource path for the prototype: 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java'

If the user asks to add any new entity or workflow, use 'add_application_resource' tool to add the new file.
If the user asks to add any new entity you should also add the corresponding workflow file.
Currently only one workflow file is supported per entity.
If the user asks to add any new workflow, you should also add the corresponding entity file.
If the user asks to modify entity or workflow, use 'add_application_resource' tool to modify the file. Then you should also modify the prototype file to reflect the changes.
Changes to the entity or workflow should be reflected in the prototype file and vice versa.
Changes to the prototype file should be reflected in the entity or workflow file and vice versa.
Changes should be propagated to the functional requirements file.

Once the user is happy with the result or has no more questions, please call finish_discussion.
Entities can be found in the file 'src/main/java/com/java_template/application/entity/{EntityName}.java'.
Workflows can be found in the file 'src/main/java/com/java_template/application/workflow/{EntityName}.json'.
Functional requirements can be found in the file 'src/main/java/com/java_template/prototype/functional_requirement.md'.
Initial user requirement can be found in the file 'src/main/java/com/java_template/prototype/user_requirement.md'.
Prototype file can be found in 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java'.
