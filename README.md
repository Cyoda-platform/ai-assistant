Building applications that support:

*Data Ingestion, Processing, and Validation

*Batch Processing and Scheduling

*User Interaction and Notification Systems

*Reporting, Analytics, and Data Aggregation

*Data Enrichment and Secondary Data Generation

*Business Logic Implementation

*System & API Integration

*Data Backup, Recovery, Export/Import


Purpose:
Summarizing data from multiple sources to provide a holistic view (e.g., aggregating sales data across multiple regions).
Ideal for generating reports, dashboards, and insights.


= 🧠 How to Run AI Assistant Locally

== 1. Set Up the Python Environment

Make sure you have Python 3.12 installed.

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

In your IDE, select this virtual environment as the Python interpreter if needed.

Install the required dependencies:

```bash
  pip install -r requirements.txt
```

== 2. Configure Environment Variables

Rename the `.env.template` file to `.env`.

Add the environment variable values provided to you.

== 3. Launch the Application

Run the application:

```bash
  python app.py
```

Check the terminal output to verify that the application starts successfully.

== ⚠️ Temporary Step (One-Time Setup)

=== 4. Convert Workflows

Run the following script to convert workflows:

```bash
  python -m common.workflow.workflow_to_dto_converter
```

This will generate the `outputs/config` directory.

=== 5. Import Workflows

Manually import all workflows from the `outputs/config` directory into your Cyoda environment.

this is a temporary inconvenience

== ✅ Done

The application should now be available and running locally.

== 🔗 UI Repository

Frontend repository: https://github.com/Cyoda-platform/ai-assistant-ui
