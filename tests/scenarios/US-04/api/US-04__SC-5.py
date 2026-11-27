# scenario-id: US-04/SC-5
"""SC-5: GET /api/employees/{id} returns employee; body.id equals seeded id."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Seed an employee to guarantee at least one exists
seed = json.dumps({
    "name": "SC5 Employee",
    "email": "sc5@test.com",
    "team": "Engineering",
    "remaining_days": 10,
}).encode()
req_create = urllib.request.Request(
    f"{base_url}/api/employees",
    data=seed,
    headers={"Content-Type": "application/json"},
    method="POST",
)
emp_id = 1
try:
    with urllib.request.urlopen(req_create) as r:
        created = json.loads(r.read().decode())
        emp_id = created.get("id", 1)
except Exception as exc:
    print(f"# seed failed: {exc}", flush=True)

# GET by id
req = urllib.request.Request(f"{base_url}/api/employees/{emp_id}")
try:
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        body = json.loads(resp.read().decode())
except urllib.error.HTTPError as e:
    status = e.code
    body = json.loads(e.read().decode())
except Exception as e:
    status = 0
    body = {"error": str(e)}

print(json.dumps({"status": status, "body": body}))
