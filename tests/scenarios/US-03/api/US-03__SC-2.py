# scenario-id: US-03/SC-2
"""SC-2: 422 validation error uses unified error JSON — body.error exists."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# POST to /api/demo/validate triggers a 422 HTTPException via the demo endpoint
req = urllib.request.Request(
    f"{base_url}/api/demo/validate",
    data=json.dumps({}).encode(),
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
