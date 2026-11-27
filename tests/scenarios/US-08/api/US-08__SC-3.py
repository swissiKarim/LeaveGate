# scenario-id: US-08/SC-3
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))

# Create an employee first
create_req = urllib.request.Request(
    base_url + "/api/employees",
    data=json.dumps({"name": "Detail User", "email": "detail@example.com", "team": "QA", "remaining_days": 15}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(create_req) as resp:
    emp = json.loads(resp.read())

emp_id = emp["id"]

# GET /employees/{id} – detail page (HTML)
url = base_url + "/employees/" + str(emp_id)
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
