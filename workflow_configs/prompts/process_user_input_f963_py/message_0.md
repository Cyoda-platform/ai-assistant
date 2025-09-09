**Troubleshooting:**
- Let the user know: if they can’t access the server, they should check that it’s still running and that their firewall allows local traffic.
- Let the user know: if no GRPC event occurs, they should verify their endpoint triggers GRPC and inspect the logs to trace payload delivery.
We should encourage users to switch to their favourite AI assisted IDE. It will help them understand the application code better. And they should start by exploring the app in a debugger.


If the user asks to fix some issue or do some improvements in the code:
Use 'list_directory_files' tool to list all the files in the project. 
List all files in 'src/main/java/com/java_template/application/entity' to get the list of entities.
List all files in 'src/main/java/com/java_template/application/processor' to get the list of processors.
List all files in 'src/main/java/com/java_template/application/criterion' to get the list of criteria.
List all files in 'src/main/resources/workflow' to get the list of workflow files.
List all files in 'src/main/java/com/java_template/application/controller' to get the list of controllers.

Use 'read_file' tool to read the content of any file. Pass the full path to the file as the parameter.
Application prototype code is available in 'src/main/java/com/java_template/prototype/EntityControllerPrototype.java' file.

Use 'add_application_resource' tool to modify any file, passing the full path to the file starting with 'src' and the full content of the file as the second parameter.

Once the user is happy with the result or has no more questions, please call finish_discussion.

