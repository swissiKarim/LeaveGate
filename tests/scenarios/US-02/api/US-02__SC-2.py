# scenario-id: US-02/SC-2
"""API scenario: POST /api/leave-requests creates a leave request with all required fields."""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Get all employees; use the first one or create a new one to get id=1
list_resp = httpx.get(f"{base_url}/api/employees", timeout=10)
employees = list_resp.json() if list_resp.status_code == 200 else []

if employees:
    # Use the first employee (id=1 when SC-1 ran before us)
    employee_id = employees[0]["id"]
else:
    # Fresh DB: create first employee → gets id=1
    emp_resp = httpx.post(
        f"{base_url}/api/employees",
        json={"name": "Alice", "email": "alice@test.com", "team": "Engineering", "remaining_days": 20},
        timeout=10,
    )
    employee_id = emp_resp.json().get("id", 1)

payload = {
    "employee_id": employee_id,
    "type": "vacation",
    "start_date": "2025-08-04",
    "end_date": "2025-08-08",
    "days": 5,
    "reason": "Summer holiday",
    "status": "draft",
}

resp = httpx.post(f"{base_url}/api/leave-requests", json=payload, timeout=10)
body = resp.json()

print(json.dumps({
    "status": resp.status_code,
    "headers": dict(resp.headers),
    "body": body,
}))
