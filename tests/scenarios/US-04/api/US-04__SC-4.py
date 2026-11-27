# scenario-id: US-04/SC-4
"""SC-4: POST /api/employees rejects missing required fields; status 422, body.error exists."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Missing name, email, team — all required
payload = json.dumps({"remaining_days": 10}).encode()

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
