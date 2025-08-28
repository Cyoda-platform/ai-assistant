
🎉 **Project Compilation Completed Successfully!**

Your prototype application has been fully generated and compiled.

📁 **Project Structure:**
```
src/main/java/com/java_template/
├── application/
│   ├── controller/     # REST API endpoints
│   ├── processor/      # Business logic
│   ├── criteria/       # Validation rules
│   └── workflow/       # Workflow configs
└── prototype/
    └── functional_requirement.md
```

🚀 **Next Steps:**
1. You can run and test it locally or directly in **GitHub Codespaces**.

### ▶️ How to Run the Prototype

#### **Option 1: GitHub Codespaces **
You can open the repo in GitHub Codespaces and launch the prototype there:

1. Open the repository in [GitHub Codespaces](https://github.com/Cyoda-platform/{repository_name}/tree/{git_branch}).
2. In the Codespace terminal, run:

```bash
# Update package list
sudo apt update
# Install Java 21 (headless — no GUI tools)
sudo apt install -y openjdk-21-jdk-headless
# Set Java 21 as active version
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
# Run the tests for processors and use debugger to step through the processors code
./gradlew test 
```

---### ✅ Approval or Feedback
If you're happy with the prototype, feel free to approve it.

If anything's off or you'd like changes, just ping me here. 🙌

Alternatively, you can use your IDE AI assistant with a suggested prompt:

**Prompt for your IDE:**
```markdown
This project is a **Cyoda client application**.

 * **Entities** (POJOs) are in `src/main/java/com/java_template/application/entity/`
 * **Workflows** (YAML/JSON configs) are in `src/main/resources/workflow/`
 * **Original user requirements** are in `src/main/java/com/java_template/prototype/user_requirement.md`
 * **Functional requirements** are in `src/main/java/com/java_template/prototype/functional_requirement.md`
 * **Controllers** (REST API endpoints) are in `src/main/java/com/java_template/application/controller/`
 * **Processors** (business logic) are in `src/main/java/com/java_template/application/processor/`
 * **Criteria** (validation rules) are in `src/main/java/com/java_template/application/criterion/`

 The system is **event-driven** — workflows define states, transitions, and criteria declaratively, without code changes.

 **Key rules:**

 1. Always review and learn from the original and functional requirement documents to fully understand the user requirements.
 2. If you update any entity or workflow, you must also update the functional requirement document.

 For detailed instructions, see `README.md` in the project root.
 The most up-to-date configuration and reference material can be loaded from the **doc server** at https://docs.cyoda.net.

Instructions:
1. Review the generated code and configuration. Fix any compilation errors.
2. Review the `prototype/functional_requirement.md` document. Make sure all the example requests and responses in the controllers are correct and up to date.
3. Review the `prototype/functional_requirement.md` document and Workflows (YAML/JSON configs). Make sure all processors and criteria are implemented correctly.
If any processors, criteria or controllers are not implemented correctly, fix the implementation.
Do not modify the workflow JSONs or entities without explicit approval.
4. Generate a report of the implemented functionality and if it matches the functional requirements.
```

If you make any changes, please share them with me in the chat or just push them to your branch and ask me to review them or just click "Approve".

> ⚠️ **Note:** This prototype runs in isolated mode with only the essential components, without authentication or gRPC dependencies.",

Please, make sure you review the code before approving and going to the next step.
