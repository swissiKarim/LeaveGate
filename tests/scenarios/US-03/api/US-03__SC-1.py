# scenario-id: US-03/SC-1
"""SC-1: 404 response uses unified error JSON — body.error and body.detail exist."""
import json
import os
import urllib.error
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

req = urllib.request.Request(f"{base_url}/api/demo/not-found")
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
