📌 Two-Way Automation Sync — Leads ↔ Tasks

Take-Home Assignment: Software Engineer Intern — Automation & Integrations

👤 Author

Vilas K N

🎯 Overview

This project implements a two-way synchronization layer between:
*Lead Tracker: Google Sheets (SaaS tool)
*Work Tracker: Custom FastAPI + SQLite microservice

The automation ensures that:
  Whenever a Lead is created in Google Sheets → a Task is created automatically in Work Tracker.
  Whenever a Task’s status is updated → the corresponding Lead’s status is updated in the Sheet.

The sync is:
  Idempotent (re-running doesn’t create duplicates)
  Event-aware
  Fully logged
  Robust with error handling

This reflects real-world internal automation that integrates SaaS tools with custom services.

🔗 Tools Integrated
                Tool	                                            Purpose
Google Sheets (via gspread + Sheets API)	              Source of truth for Leads
FastAPI	                                                Work Tracker API for tasks
SQLite	                                            Lightweight DB for storing tasks
Python (requests + FastAPI + gspread)	                  Automation + integrations


🧩 Architecture & Flow
+-------------------+             +-----------------------+
|   Google Sheets   | <---------> |   sync.py (Python)    |
|  (Lead Tracker)   |    API      | Two-way Sync Engine   |
+-------------------+             +-----------+-----------+
                                            |
                                            | REST
                                            v
                                  +----------------------+
                                  | FastAPI Work Tracker |
                                  | (SQLite Task Store)  |
                                  +----------------------+

High-level Flow:
  1)Lead → Task:
          *If a lead has no task_id → sync creates a Task in FastAPI.
          *Writes the task ID back into the Google Sheet.
          *Ensures idempotency.

  2)Task → Lead:
          *If a task status is updated (todo → done) → sync updates lead status in the sheet.


🏗️ Setup Instructions
  1️⃣ Google Sheets Setup:
        *Create a new sheet with headers:
            lead_id | name | email | status | task_id
        *Fill a few sample rows.
        *Create a Google Cloud project
        *Enable:
            Google Sheets API
            Google Drive API
        *Create a Service Account → generate JSON key.
        *Share your Sheet with the service account email (Editor access).
        *Add your key as:
          service_account.json

  2️⃣ Work Tracker API Setup (FastAPI)
      Install dependencies:

pip install -r requirements.txt


Run the API:

uvicorn app.main:app --reload


Open docs:
👉 http://127.0.0.1:8000/docs

3️⃣ Configure Environment

Place your service account key as:

service_account.json


Project includes a placeholder file:

service_account.example.json

4️⃣ Running the Sync Engine
python -m integrations.sync

▶️ Usage Guide (How to Test)
1️⃣ Lead → Task (Create a lead → Task appears)

Add a new row in Google Sheets:

3 | Charlie | charlie@example.com | new | 


Run:

python -m integrations.sync


A corresponding task appears in FastAPI:

GET /tasks


The task_id column in the Sheet is updated automatically.

2️⃣ Task → Lead (Update a task → Lead status updates)

Open FastAPI docs → PUT /tasks/{task_id}

Send:

{
  "status": "done"
}


Run:

python -m integrations.sync


Google Sheet status changes to:

completed

⚙️ Error Handling

The sync uses:

try:
    r = requests.post(...)
    r.raise_for_status()
except requests.RequestException as e:
    logger.error(...)


Covers:

Invalid API calls

Network issues

Incorrect credentials

Missing rows in the sheet

All errors are logged clearly.

🔁 Idempotency Strategy

To avoid duplicate tasks:

Every Lead stores the task_id

Sync logic:

if task_id exists:
    update task ONLY
else:
    create new task


Re-running the sync produces stable, repeatable, deterministic results.
