
Your requirement has been added to the `src/main/resources/functional_requirements` directory.

Would you like to refine or extend the functional requirements and API? If so, please edit the requirement files directly.

Once you’ve made your edits, push the changes to the repository.

* If you don’t yet have access, request it by posting:
  *“Please give me access to the repository. My GitHub username is {github_username}.”*

I’m always open to feedback or ideas — happy to hear your thoughts 👂 (well… mostly 😏).

Feel free to use your IDE’s AI agents to help with implementation. The prompt I recommend using to check the requirement is:

```markdown
You are provided with already generated functional requirement files under `src/main/resources/functional_requirements` and corresponding workflow JSONs in src/main/resources/workflow.

**Task:** Do *not* regenerate. Instead, **review and validate** correctness, completeness, and consistency against:

* `user_requirement.md`
* `user_requirement_additional_info.md`

#### Checks

1. **Entities** – Attributes, relationships, and state handling (`entity.meta.state` only).
2. **Workflows** – States, transitions (initial→first auto, loops manual), processors/criteria minimal & valid. Mermaid diagram + pseudocode present.
3. **Workflow JSON** – Matches workflow diagram exactly. Validates against `llm_example/config/workflow/workflow_schema.json`.
4. **Controllers** – Endpoints align with workflows; transitions consistent; full request/response examples.
5. **Acceptance** – `./gradlew validateFunctionalRequirements` passes, or issues are clearly identified.
6. **Consistency** – Highlight missing, redundant, or misinterpreted elements. Suggest fixes, don’t rewrite wholesale.

**Output:** Provide a structured summary of gaps, inconsistencies, and recommended fixes.
```
 