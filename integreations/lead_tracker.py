
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

#name of credentials file
SERVICE_ACCOUNT_FILE = "service_account.json"

SHEET_NAME = "LeadTracker"

def get_sheet():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1  # first worksheet
    return sheet

def get_all_leads():
    """
    Returns a list of leads as dicts:
    [
      {"lead_id": "1", "name": "Alice", "email": "...", "status": "new", "task_id": ""},
      ...
    ]
    """
    sheet = get_sheet()
    rows = sheet.get_all_records()  # list of dicts based on header row
    return rows

def update_lead_task_id(lead_id: str, task_id: str):
    """
    Find the row with given lead_id and set task_id column.
    """
    sheet = get_sheet()
    data = sheet.get_all_records()
    # Rows in sheet start from 2 (row 1 is header)
    for idx, row in enumerate(data, start=2):
        if str(row["lead_id"]) == str(lead_id):
            # Find column index of task_id
            headers = sheet.row_values(1)
            task_id_col = headers.index("task_id") + 1  # 1-based index
            sheet.update_cell(idx, task_id_col, task_id)
            break

def update_lead_status(lead_id: str, new_status: str):
    """
    Find the row with given lead_id and set status column.
    """
    sheet = get_sheet()
    data = sheet.get_all_records()
    for idx, row in enumerate(data, start=2):
        if str(row["lead_id"]) == str(lead_id):
            headers = sheet.row_values(1)
            status_col = headers.index("status") + 1
            sheet.update_cell(idx, status_col, new_status)
            break
