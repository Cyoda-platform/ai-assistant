<p align="center">
  <img src="assets/logo.png" alt="AI Assistant Logo" width="150" />
</p>
<h1 align="center">AI Assistant</h1>

<p align="center">
  <strong>
    Build, deploy and scale data-intensive operational services.
  </strong><br/>
  Cyoda’s AI Assistant creates complete prototype backend services for the <a href="https://www.cyoda.com/application-platform">Cyoda Application Platform</a>.<br/>
  It automates entity design, workflows, processes, rules, and queries, enabling developers to build scalable services 20× faster.
</p>

---

## 🔗 Quick Links

- [Features](#-features)
- [Setup (for Local Use)](#-setup-for-local-use)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up the Python Environment](#2-set-up-the-python-environment)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
- [Workflow Setup (One-Time)](#-workflow-setup-one-time)
  - [4. Convert Workflows](#4-convert-workflows)
  - [5. Import Workflows to Cyoda](#5-import-workflows-to-cyoda)
- [Run the Backend Application](#-run-the-backend-application)
- [Run the UI](#-run-the-ui)
- [Project Structure](#-project-structure)
- [AI Model Configuration (Optional)](#-ai-model-configuration-optional)
- [License](#-license)
- [Support](#-support)

---

## 🚀 Features

Building applications that support:

- Data Ingestion, Processing, and Validation
- Batch Processing and Scheduling
- User Interaction and Notification Systems
- Reporting, Analytics, and Data Aggregation
- Data Enrichment and Secondary Data Generation
- Business Logic Implementation
- System & API Integration
- Data Backup, Recovery, Export/Import

Purpose:
Summarizing data from multiple sources to provide a holistic view (e.g., aggregating sales data across multiple regions).  
Ideal for generating reports, dashboards, and insights.

---

## 🔨 Setup (for Local Use)
*Prefer using the assistant locally to keep your projects private.*

### 📦 Prerequisites

- Python 3.12
- Git
- Access to Cyoda environment
- API keys for:
  - AI provider (e.g. OpenAI)
  - Search API provider (if used)

### 1. Clone the Repository

```bash
git clone https://github.com/Cyoda-platform/ai-assistant.git
cd ai-assistant
```

### 2. Set Up the Python Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Note**: After creating and activating the virtual environment (venv) via the terminal,  
you may need to manually select this venv as the Python interpreter in your IDE (e.g., PyCharm, VSCode).  
This ensures that IDE features like Run, Debug, and code completion work correctly with the project environment.

### 3. Configure Environment Variables

Rename `.env.template` to `.env`:

```bash
cp .env.template .env
```

Fill in the required variables:

```env
# Example
CYODA_API_KEY=your_cyoda_key
CYODA_API_SECRET=your_cyoda_secret
CYODA_HOST=your_cyoda_host
OPENAI_API_KEY=your_openai_key
PROJECT_DIR=/home/yourname/projects
```

---

## 📄 Workflow Setup (One-Time)

⚠️ Temporary Step

### 4. Convert Workflows

Convert workflow JSONs to Cyoda DTO format:

```bash
python -m common.workflow.workflow_to_dto_converter
```

This generates output files in the `outputs/config` folder.

**Note:** This manual step will be removed in future versions.

### 5. Import Workflows to Cyoda

Manually import all workflows from the `outputs/config` directory into your Cyoda environment.

---

## 💡 Run the Backend Application

```bash
python app.py
```

✅ Done. The application will be available at http://localhost:5000.

---

## 💻 Run the UI

Clone and run the [AI Assistant UI](https://github.com/Cyoda-platform/ai-assistant-ui) project:

```bash
git clone https://github.com/Cyoda-platform/ai-assistant-ui
cd ai-assistant-ui
```
For detailed setup and running instructions, please refer to the [AI Assistant UI README](https://github.com/Cyoda-platform/ai-assistant-ui#readme).

---

## 📁 Project Structure

```text
ai-assistant/
├── app.py                              # Entry point of the application
├── requirements.txt                    # Python dependencies
├── .env.template                       # Example environment configuration

├── entity/                             
│   └── model.py                        # Configuration schema for model selection

├── common/                             # Core logic and modules
│   └── workflow/                       # Workflows and workflow tools
│       ├── config/                     # Workflow files (to be converted)
│       │   └── example_workflow.json   # Example source workflow
│       ├── outputs/                    # Converted files (e.g., DTOs)
│       │   └── example_output.json     # Example converted output
│       └── workflow_to_dto_converter.py # Converts workflows to DTO format
```

---

## 🧠 AI Model Configuration (Optional)

You can configure which AI model is used to process AI-powered transitions in two ways:

### 1. Set the Default Model and Parameters

The default model configuration is defined in the `ModelConfig` class (`entity/model.py`).  
You can customize:

- The default model name (`model_name`)
- Temperature, top-p, max tokens, penalties

Example default configuration:

```python
# Define allowed model names
ModelName = Literal[
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gpt-4o",
    "gpt-4.1-nano",
    "o4-mini"
]

class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    model_name: ModelName = Field(
        default="gpt-4.1-mini",  # Change this line to set the default model
        description="Name of the model to use"
    )
    temperature: float = 0.7
    max_tokens: int = 10000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
```

This configuration will be used for all transitions **unless overridden explicitly**.

---

### 2. Override the Model per Transition

In each workflow `transition` that uses the `"prompt"` or `"agent"` action type, you can override the model by passing a custom `model` section in the config.

Example:

```json
"action": {
  "name": "process_event",
  "config": {
    "type": "agent",
    "model": {
      "model_name": "o4-mini",
      "temperature": 0.3,
      "max_tokens": 5000
    },
    "input": {},
    "output": {}
  }
}
```

Only the fields you specify will override the defaults.  
If `model` is omitted or left empty (`"model": {}`), the default `ModelConfig` is used.

---

## 📚 License

This project is licensed under the Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

---

## 💬 Support

For the fastest help and direct communication, join our [Discord community](https://discord.gg/95rdAyBZr2).  
You can also open an issue or pull request here on GitHub for bugs or contributions.