# scenario-id: US-04/SC-5
"""SC-5: GET /api/employees/{id} returns employee; body.id equals 1."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Ensure at least one employee exists with id=1 by creating one first if needed.
# In the verify sandbox each scenario runs against the same live service, so
# earlier scenarios (SC-1..SC-4) may have already created employees. We just
# need to fetch id=1 which is guaranteed to exist after at least one creation.
# As a safety net, seed one employee; if the service already has id=1, the
# GET will still return it.
seed = json.dumps({
    "name": "SC5 Seed",
    "email": "sc5.seed@test.com",
    "team": "Engineering",
    "remaining_days": 10,
}).encode()
req_seed = urllib.request.Request(
    f"{base_url}/api/employees",
    data=seed,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req_seed) as r:
        pass
except Exception as exc:
    print(f"# seed info: {exc}", flush=True)

# Always GET /api/employees/1 — the platform then-check is body.id equals 1
req = urllib.request.Request(f"{base_url}/api/employees/1")
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
