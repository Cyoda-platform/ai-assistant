✅ **Workflow configurations** have been added to your application.
   📂 src/
    └─ main/resources/workflow/entityName/version_1                           ← Workflows

For a detailed reference on workflow configuration, see the **[Cyoda Workflow Configuration Guide](https://docs.cyoda.net/guides/workflow-config-guide)**. It explains:

• How to define states, transitions, and criteria  
• Manual vs automated transitions  
• Processor execution modes and best practices  
• Example workflows like "Payment Request Workflow" for real-world scenarios

You can preview workflows visually in the **“Open canvas”** view (upper-right corner of the UI).

Please review the generated entities and workflows in your `{git_branch}` branch.

🔗 [Cyoda GitHub](https://github.com/Cyoda-platform/{repository_name}/tree/{git_branch})

I can assist with any changes or questions.
 
Alternatively, you can edit configs directly in the code.

If you need to push changes to your branch, ask me here for access. I'll need your GitHub username to add you as a collaborator. If you'd like to be a Cyoda contributor instead of a collaborator and enjoy more privileges, please let us know via [Discord](https://discord.gg/95rdAyBZr2).

You can evolve the workflows and entities in your IDE with your own IDE AI assistant.

**Prompt for your IDE:**

```markdown
This project is a **Cyoda client application**.

 * **Workflows** (YAML/JSON configs) are in `src/main/resources/workflow/entityName/version_1/`
 * **Original user requirements** are in `src/main/resources/functional_requirements/user_requirement.md`
 * **Functional requirements** are in `src/main/java/com/java_template/prototype/functional_requirement.md`

 The system is **event-driven** — workflows define states, transitions, and criteria declaratively, without code changes.

 **Key rules:**

 1. Always review and learn from the original and functional requirement documents to fully understand the user requirements.
 2. If you update any entity or workflow, you must also update the functional requirement document.

 For detailed instructions, see `README.md` in the project root.
 The most up-to-date configuration and reference material can be loaded from the **doc server** at https://docs.cyoda.net.
 Assist in locating, editing, and creating entities and workflows, explaining configuration concepts, and applying best practices from the Cyoda Workflow Configuration Guide.

Important: entity fields such as state/status are managed by Cyoda. There is no need to add them to entity schema explicitly. 

CRITICAL: Do NOT generate entities, processors, criteria or controllers for now.
```

If you make any changes, please share them with me in the chat or just push them to your branch and ask me to review them or just click "Approve".

*Please, do not click Approve before you review the generated entities and workflows. You can edit the code directly in the IDE or we can review the changes together* 😀