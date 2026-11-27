# scenario-id: US-04/SC-2
"""SC-2: GET /api/employees supports q, sort and page parameters; body.items[0].name contains "Alice"."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Seed an employee named Alice
seed = json.dumps({"name": "Alice Query", "email": "alice.query@test.com", "team": "Engineering", "remaining_days": 15}).encode()
req = urllib.request.Request(
    f"{base_url}/api/employees",
    data=seed,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req) as r:
        pass
except Exception as exc:
    print(f"# seed failed: {exc}", flush=True)

# GET with q, sort and page parameters
req2 = urllib.request.Request(f"{base_url}/api/employees?q=Alice&sort=name&page=1")
try:
    with urllib.request.urlopen(req2) as resp:
        status = resp.status
        body = json.loads(resp.read().decode())
except urllib.error.HTTPError as e:
    status = e.code
    body = json.loads(e.read().decode())
except Exception as e:
    status = 0
    body = {"error": str(e)}

print(json.dumps({"status": status, "body": body}))
