# scenario-id: US-02/SC-2
"""API scenario: POST /api/leave-requests creates a leave request with all required fields."""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# First ensure employee with id=1 exists (create if needed)
emp_resp = httpx.post(
    f"{base_url}/api/employees",
    json={"name": "Bob", "email": "bob@test.com", "team": "Engineering", "remaining_days": 25},
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
