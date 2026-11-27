# scenario-id: US-04/SC-1
"""SC-1: GET /api/employees returns list with filter support; body.items[0].team == "Engineering"."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Seed an Engineering employee first
seed = json.dumps({"name": "Alice Engineering", "email": "alice.eng@test.com", "team": "Engineering", "remaining_days": 15}).encode()
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

# GET with team filter
req2 = urllib.request.Request(f"{base_url}/api/employees?team=Engineering")
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
