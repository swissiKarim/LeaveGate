# scenario-id: US-07/SC-5
"""SC-5: Focus-visible styles are defined in stylesheet."""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

try:
    with urllib.request.urlopen(f"{base_url}/") as resp:
        status = resp.status
        body = resp.read().decode("utf-8")
except Exception as e:
    status = 0
    body = str(e)

print(json.dumps({"status": status, "body": body}))
