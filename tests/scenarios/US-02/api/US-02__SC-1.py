# scenario-id: US-02/SC-1
"""API scenario: POST /api/employees creates an employee with all required fields."""
import json
import os

import httpx

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

payload = {
    "name": "Alice",
    "email": "alice@test.com",
    "team": "Engineering",
    "remaining_days": 20,
}

resp = httpx.post(f"{base_url}/api/employees", json=payload, timeout=10)

print(json.dumps({
    "status": resp.status_code,
    "headers": dict(resp.headers),
    "body": resp.json(),
}))
