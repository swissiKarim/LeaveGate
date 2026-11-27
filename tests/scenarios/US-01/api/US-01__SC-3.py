# scenario-id: US-01/SC-3
"""SC-3: GET /docs returns HTTP 200."""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

req = urllib.request.Request(f"{base_url}/docs")
try:
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        body = resp.read().decode()
except Exception as e:
    status = 0
    body = str(e)

print(json.dumps({"status": status, "body": body}))
