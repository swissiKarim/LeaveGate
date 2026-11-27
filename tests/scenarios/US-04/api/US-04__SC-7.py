# scenario-id: US-04/SC-7
"""SC-7: PATCH /api/employees/{id} updates and returns employee; body.remaining_days == 10."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Seed an employee
seed = json.dumps({
    "name": "SC7 Employee",
    "email": "sc7@test.com",
    "team": "Engineering",
    "remaining_days": 20,
}).encode()
req_create = urllib.request.Request(
    f"{base_url}/api/employees",
    data=seed,
    headers={"Content-Type": "application/json"},
    method="POST",
)
emp_id = None
try:
    with urllib.request.urlopen(req_create) as r:
        created = json.loads(r.read().decode())
        emp_id = created.get("id")
except Exception as exc:
    print(f"# seed failed: {exc}", flush=True)

status = 0
body: dict = {"error": "could not create employee"}

if emp_id is not None:
    patch_payload = json.dumps({"remaining_days": 10}).encode()
    req_patch = urllib.request.Request(
        f"{base_url}/api/employees/{emp_id}",
        data=patch_payload,
        headers={"Content-Type": "application/json"},
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req_patch) as resp:
            status = resp.status
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        status = e.code
        body = json.loads(e.read().decode())
    except Exception as e:
        status = 0
        body = {"error": str(e)}

print(json.dumps({"status": status, "body": body}))
