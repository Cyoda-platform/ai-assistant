
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
# Run the prototype app
./gradlew test --tests PrototypeApplicationTest -Dprototype.enabled=true
```
3. Make the app accessible from the browser:
- In the **Ports** panel (bottom of the IDE), right-click on port `8081` and select **Change Port Visibility → Public**
- Alternatively, after starting the app, click **Make Public** in the popup.

4. Preview the app in the browser:
`/swagger-ui/index.html` - Swagger UI: `https://<your-codespace-url>/swagger-ui/index.html`
- OpenAPI specification: `https://<your-codespace-url>/v3/api-docs`> 
*Codespaces will provide a forwarded port URL — just append `/swagger-ui/index.html` or `/v3/api-docs` to it.*

---#### **Option 2: Local Environment**

1. Make sure you're on the correct branch and up to date:

```bash
git checkout {git_branch}
git pull
```

2. Run the prototype app:

```bash
./gradlew test --tests PrototypeApplicationTest -Dprototype.enabled=true
```
3. Open your browser and go to:
- [http://localhost:8081/swagger-ui/index.html](http://localhost:8081/swagger-ui/index.html)
- or [http://localhost:8081/v3/api-docs](http://localhost:8081/v3/api-docs)
---### 🧪 Testing
You'll find example requests and responses in:
📄 `prototype/functional_requirement.md`
Use these to test the API via the Swagger UI.
---### ✅ Approval or Feedback
If you're happy with the prototype, feel free to approve it.

If anything's off or you'd like changes, just ping me here. 🙌
> ⚠️ **Note:** This prototype runs in isolated mode with only the essential components, without authentication or gRPC dependencies.",


**Click approve to continue the discussion.**
