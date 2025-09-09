Please, adjust the functional requirements, entities and workflows and the API according to the user request. 
Use 'list_directory_files' tool to list all the files in the project. 
List all files in 'resources/workflow' to get the list of workflows.

Use 'read_file' tool to read the content of any file. Pass the full path to the file as the parameter.

Use 'add_application_resource' tool to modify any file, passing the full path to the file and the full content of the file as the second parameter.
Pass resource_path as the first parameter and file_contents as the second parameter.
Resource path for the workflows: 'resources/workflow/{entityname}/version_1/{EntityName}.json'

If the user asks to add any new entity or workflow, use 'add_application_resource' tool to add the new file.
If the user asks to add any new entity you should also add the corresponding workflow file.
Currently only one workflow file is supported per entity.

Once the user is happy with the result or has no more questions, please call finish_discussion.
Functional requirements can be found in the file 'functional_requirements/functional_requirement.md'.

Do your best to help the user with their request:
