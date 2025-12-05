# integrations/sync.py
import logging
import requests

from .lead_tracker import get_all_leads, update_lead_task_id, update_lead_status

# URL of your Work Tracker API
WORK_TRACKER_BASE_URL = "http://127.0.0.1:8000"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---- Helpers to call Work Tracker API ----

def create_task_for_lead(lead):
    """
    lead is a dict from Google Sheets, e.g.:
    {"lead_id": "1", "name": "Alice", "email": "...", "status": "new", "task_id": ""}
    """
    url = f"{WORK_TRACKER_BASE_URL}/tasks"
    payload = {
        "lead_id": str(lead["lead_id"]),
        "title": f"Follow up: {lead['name']} ({lead['email']})",
        "status": map_lead_status_to_task_status(lead["status"]),
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        task = r.json()
        logger.info(f"Created task {task['id']} for lead {lead['lead_id']}")
        return task
    except requests.RequestException as e:
        logger.error(f"Failed to create task for lead {lead['lead_id']}: {e}")
        return None

def update_task(task_id: int, fields: dict):
    url = f"{WORK_TRACKER_BASE_URL}/tasks/{task_id}"
    try:
        r = requests.put(url, json=fields, timeout=10)
        r.raise_for_status()
        task = r.json()
        logger.info(f"Updated task {task_id} with {fields}")
        return task
    except requests.RequestException as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        return None

def get_all_tasks():
    url = f"{WORK_TRACKER_BASE_URL}/tasks"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch tasks: {e}")
        return []

# ---- Status mapping logic ----

def map_lead_status_to_task_status(lead_status: str) -> str:
    """
    Simple mapping for demo. You can tweak as needed.
    """
    lead_status = (lead_status or "").lower()
    if lead_status in ("new", "contacted"):
        return "todo"
    if lead_status in ("in_progress", "demo_scheduled"):
        return "in_progress"
    if lead_status in ("completed", "done", "closed"):
        return "done"
    return "todo"

def map_task_status_to_lead_status(task_status: str) -> str:
    task_status = (task_status or "").lower()
    if task_status == "todo":
        return "new"
    if task_status == "in_progress":
        return "in_progress"
    if task_status == "done":
        return "completed"
    return "new"

# ---- Sync logic ----

def sync_leads_to_tasks():
    """
    For each lead in Google Sheets:
      - If it has no task_id: create a new task in Work Tracker, store task_id in sheet.
      - If it has a task_id: do NOT overwrite the task's status.
        (We treat the Work Tracker as the source of truth for status.)
    """
    leads = get_all_leads()
    logger.info(f"Fetched {len(leads)} leads from sheet")

    for lead in leads:
        lead_id = str(lead["lead_id"])
        task_id = str(lead["task_id"]) if lead["task_id"] is not None else ""

        if not task_id:
            # No task yet → create one
            logger.info(f"No task for lead {lead_id}, creating...")
            task = create_task_for_lead(lead)
            if task:
                update_lead_task_id(lead_id, str(task["id"]))
        else:
            # Task exists → we don't override its status from lead.
            logger.info(
                f"Lead {lead_id} already has task {task_id}; "
                "skipping status update (task is source of truth for status)."
            )


def sync_tasks_to_leads():
    """
    For each task in Work Tracker:
      - Find the corresponding lead by lead_id.
      - Update lead.status in sheet based on task.status.
    """
    tasks = get_all_tasks()
    logger.info(f"Fetched {len(tasks)} tasks from Work Tracker")

    for task in tasks:
        lead_id = str(task["lead_id"])
        new_lead_status = map_task_status_to_lead_status(task["status"])
        logger.info(
            f"Syncing task {task['id']} (status={task['status']}) "
            f"to lead {lead_id} (status={new_lead_status})"
        )
        update_lead_status(lead_id, new_lead_status)

if __name__ == "__main__":
    logger.info("Starting two-way sync...")
    sync_leads_to_tasks()
    sync_tasks_to_leads()
    logger.info("Sync completed.")
