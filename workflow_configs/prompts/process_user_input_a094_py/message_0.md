
    **Troubleshooting:** Let the user know: if the import fails, they should verify their JSON formats and version compatibility, and check the Cloud logs for detailed import errors.
    
    If the user asks to fix some issue or do some improvements in the code:
Use 'list_directory_files' tool to list all the files in the project. 
List all files in 'application/entity' to get the list of entities.
List all files in 'application/processor' to get the list of processors.
List all files in 'application/criterion' to get the list of criteria.
List all files in 'application/resources/workflow' to get the list of workflow files.
List all files in 'application/routes' to get the list of controllers.

Use 'add_application_resource' tool to modify any file, passing the full path to the file starting with 'src' and the full content of the file as the second parameter.

Once the user is happy with the result or has no more questions, please call finish_discussion.

    