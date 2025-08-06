"""
PromptSentF4c8PromptConfig Configuration

Generated from config: workflow_configs/prompts/prompt_sent_f4c8/message_0.md
Configuration data for the prompt.
"""

from typing import Any, Dict, Callable


def get_config() -> Callable[[Dict[str, Any]], str]:
    """Get prompt configuration factory"""
    return lambda params=None: """Let the user know: they can run the application in two ways — either directly from Gradle or by building and running the JAR manually.
Let the user know: to run the app using Gradle, they should execute `./gradlew runApp`.
Let the user know: to run the app manually, they should first build it using `./gradlew build` and then run `java -jar build/libs/java-client-template-1.0-SNAPSHOT.jar`.
Let the user know: the app will be available at `http://localhost:8080/swagger-ui/index.html` once it starts.
Let the user know: they must have Java 21 installed and set as the active version.
Let the user know: they should be in the root directory of the project (`java-client-template`) before running any commands.
Let the user know: if they encounter a `ClassNotFoundException`, they should ensure all dependencies are declared in `build.gradle`.
Let the user know: if dependencies are missing, they can run `./gradlew --refresh-dependencies` to resolve them.
 Setting values at .env file: 
- Let the user know: a default value is used for `GRPC_PROCESSOR_TAG` (they can change it if they like).
- Let the user know: if they are using shared environment they need to make sure they specify unique ENTITY_VERSION."""
