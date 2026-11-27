# scenario-id: US-04/SC-3
"""SC-3: POST /api/employees creates employee and returns 201; body.id exists, body.name == "Carol"."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

payload = json.dumps({
    "name": "Carol",
    "email": "carol@test.com",
    "team": "HR",
    "remaining_days": 15,
}).encode()

req = urllib.request.Request(
    f"{base_url}/api/employees",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
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
