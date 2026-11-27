# scenario-id: US-01/SC-1
"""SC-1: FastAPI app starts and exports app instance — GET / returns 200."""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

req = urllib.request.Request(f"{base_url}/health")
try:
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        body = json.loads(resp.read().decode())
except OSError as e:
    status = 0
    body = {"error": str(e)}

print(json.dumps({"status": status, "body": body}))
