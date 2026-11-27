# scenario-id: US-08/SC-2
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# First create an employee named Alice so the filter returns her
create_req = urllib.request.Request(
    base_url + "/api/employees",
    data=json.dumps({"name": "Alice", "email": "alice@example.com", "team": "Engineering", "remaining_days": 20}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    urllib.request.urlopen(create_req)
except Exception:  # noqa: S110
    pass  # may already exist or ignore error

# Now GET /employees?q=Alice – filter param preserved in URL
url = base_url + "/employees?q=Alice"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    status = resp.status
    body_bytes = resp.read()

body_text = body_bytes.decode("utf-8", errors="replace")

print(json.dumps({
    "status": status,
    "headers": {},
    "body": body_text,
}))
