Let the user know: with their env configured, they should import the workflows using one of the following options:

**Option 1: Run via Gradle (recommended for local development)**
```bash
./gradlew runApp -PmainClass=com.java_template.common.tool.WorkflowImportTool
```

**Option 2: Build and run the JAR file (recommended for CI or scripting)**
```bash
./gradlew bootJarWorkflowImport
java -jar build/libs/java-client-template-1.0-SNAPSHOT-workflow-import.jar
```
Let the user know: the workflows are available in `src/main/java/com/java_template/application/workflow`
Let the user know: the workflows should appear in their Cyoda UI once the import completes.
Let the user know: they can view and edit their workflow configurations here in canvas. They need to open canvas in upper right corner and chooose workflow tab. There they can view the workflow and also use AI for editing if necessary.