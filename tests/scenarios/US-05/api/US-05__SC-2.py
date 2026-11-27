# scenario-id: US-05/SC-2
"""SC-2: Valid status transition submitted→approved is allowed."""
import json
import os
import urllib.request

base_url = os.environ.get("ASB_SVC_WEB_URL", os.environ.get("ASB_API_BASE", "http://localhost:8080"))


def _post(url, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


status, emp = _post(f"{base_url}/api/employees",
                    {"name": "SC2 Emp", "email": "sc2@x.com", "team": "Dev", "remaining_days": 20})
status, lr = _post(f"{base_url}/api/leave-requests",
                   {"employee_id": emp["id"], "type": "sick",
                    "start_date": "2025-09-01", "end_date": "2025-09-05"})
_post(f"{base_url}/api/leave-requests/{lr['id']}/status", {"status": "submitted"})
status, body = _post(f"{base_url}/api/leave-requests/{lr['id']}/status", {"status": "approved"})

print(json.dumps({"status": status, "body": body}))
